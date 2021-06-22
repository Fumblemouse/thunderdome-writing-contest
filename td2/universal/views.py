""""
Views for public (non-logged-in functionality)
"""

from random import sample

from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Min, F, Sum


from baseapp.utils import set_expirable_var, get_expirable_var, get_expirable_var_time_to_del

from baseapp.models import Story, StoryStats

from .models import MiniDome
from .forms import MiniDomePublicForm, MiniDomeLoggedInForm





# Create your views here.

def minidome(request):
    """
    publicly decided ranking between two stories
    First story is random from all stories
    second story is random from those with fewer test than first story
    Process:
        test if already judged (redirect if have)
        test if logged in (wider selection if logged in)
        deliver form
    """

    judged_recently = get_expirable_var(request.session, 'minidome_judged', None)
    if judged_recently:
        ttl = get_expirable_var_time_to_del(request.session, 'minidome_judged')
        messages.error(request, 'Go home, judge, you\'re drunk with power. Time until soberiety: ' + str(int(ttl)) + ' seconds')
        return redirect('home')

    logged_in = request.user.is_authenticated

    #check to see if user has already had stories chosen
    #if request.session.get('minidome_stories', False):
    story_ids = get_expirable_var(request.session, 'minidome_stories', None)
    if story_ids is not None:
        story1 = Story.objects.get(pk = story_ids[0])
        story2 = Story.objects.get(pk = story_ids[1])
        stories_options = [story1, story2]

        if logged_in:
            form = MiniDomeLoggedInForm( [story1.pk, story2.pk], request.POST or None )
        else:
            form = MiniDomePublicForm( [story1.pk, story2.pk], request.POST or None )

    if request.method == "POST":
        if form.is_valid():
            #first we update the minidome
            form_uncommitted = form.save(commit = False)

            if logged_in:
                minidome_type = MiniDome.LOGGED_IN
            else:
                minidome_type = MiniDome.PUBLIC

            winner = form.cleaned_data.get('winner')
            stories_options.remove(winner)
            form_uncommitted.loser = stories_options[0]
            form_uncommitted.minidome_type = minidome_type
            form_uncommitted.save()
            expire_at = datetime.today() + timedelta(minutes=30)
            set_expirable_var(request.session, 'minidome_judged', True, expire_at)
            messages.success(request, 'Your judgement is final. No further corresepndance may be entered into.')
            return redirect('home')


    else :
        #decide stories in match
        if logged_in:
            min_tests = StoryStats.objects.all().aggregate(min_tests=Min(F('minidome_logged_in_wins') + F('minidome_logged_in_losses')))
            min_tests_value = min_tests['min_tests']
            if min_tests_value is None:
                messages.error(request, 'Not enough stories')
                return redirect('home')

            #Create list of stories that exceed lowest 
            #number of matches
            stories1 = list(Story.objects.filter(access__gte=1).\
                exclude(author = request.user).\
                annotate(total_logged_in_tests=F('stats__minidome_logged_in_wins') + F('stats__minidome_logged_in_losses')).\
                filter(total_logged_in_tests__gt=min_tests_value))

            #redo it if there are none (no matches so far or everyone is equal for some reason)
            if len(stories1) == 0 :
                stories1 = list(Story.objects.filter(access__gte=1).\
                    exclude(author = request.user).\
                    annotate(total_logged_in_tests=F('stats__minidome_logged_in_wins') + F('stats__minidome_logged_in_losses')).\
                    filter(total_logged_in_tests__gte=min_tests_value))

                if len(stories1) <= 1 : #because that's itself
                    messages.error(request, 'Not enough stories')
                    return redirect('home')

                stories = sample(stories1, 2)
                story1 = stories[0]
                story2 = stories[1]

            else:

                #Get number of matches of story and then choose from list of stories that have same or less.
                story1 = sample(stories1, 1)[0]
                story1_stats = StoryStats.objects.get(pk = story1.pk)
                story1_total_logged_in_tests = story1_stats.get_minidome_total_logged_in_tests()
                stories2 = list(Story.objects.filter(access__gte=1).\
                    exclude(author = request.user).\
                    annotate(total_logged_in_tests=F('stats__minidome_logged_in_wins') + F('stats__minidome_logged_in_losses')).\
                    filter(total_logged_in_tests__lt=story1_total_logged_in_tests ))
 
                story2 = sample(stories2, 1)[0]

            form = MiniDomeLoggedInForm( [story1.pk, story2.pk] )

        else: #Public match
            #find lowest number of public matches
            min_tests = StoryStats.objects.all().aggregate(min_tests=Min(F('minidome_public_wins') + F('minidome_public_losses')))
            min_tests_value = min_tests['min_tests']
            if min_tests_value is None:
                messages.error(request, 'Not enough stories')
                return redirect('home')
            #Create list of stories that exceed or equal lowestnumber of matches
            stories1 = list(Story.objects.filter(access__gte=2).\
                annotate(total_logged_in_tests=F('stats__minidome_public_wins') + F('stats__minidome_public_losses')).\
                filter(total_logged_in_tests__gt=min_tests_value))
             #redo it if there are none (no matches so far or everyone is equal for some reason)
            if len(stories1) == 0 :
                stories1 = list(Story.objects.filter(access__gte=2).\
                annotate(total_logged_in_tests=Sum(F('stats__minidome_public_wins') + F('stats__minidome_public_losses'))).\
                filter(total_logged_in_tests__gte=min_tests_value))    
                
                
                if len(stories1) <= 1 : #because that's itself
                    messages.error(request, 'Not enough stories')
                    return redirect('home')
                stories = sample(stories1, 2)
                story1 = stories[0]
                story2 = stories[1]
            else:
                #Get number of matches of story and then choose from list of stories that have same or less.
                story1 = sample(stories1, 1)[0]
                story1_stats = StoryStats.objects.get(pk = story1)
                story1_total_public_tests = story1_stats.get_minidome_total_public_tests()

                #stories2 = list(Story.objects.filter(access__gte=2).filter(stats__minidome_total_public_tests__lt = story1_stats.minidome_total_public_tests))
                stories2 = list(Story.objects.filter(access__gte=2).\
                annotate(total_logged_in_tests=Sum(F('stats__minidome_public_wins') + F('stats__minidome_public_losses'))).\
                filter(total_logged_in_tests__lt=story1_total_public_tests))
                
                story2 = sample(stories2, 1)[0]

            form = MiniDomePublicForm( [story1.pk, story2.pk] )

    story1_context = story1
    story2_context = story2

    expire_at = datetime.today() + timedelta(minutes=30)
    set_expirable_var(request.session, 'minidome_stories', [story1.pk, story2.pk], expire_at)


    return render(request, 'universal/minidome.html', {
        'story2_context' : story2_context,
        'story1_context' : story1_context,
        'form': form,
        }
    )
