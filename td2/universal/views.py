""""
Views for public (non-logged-in functionality)
"""

from random import sample

from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Min

from baseapp.models import Story, StoryStats
from .forms import MiniDomePublicForm, MiniDomeLoggedInForm





# Create your views here.

def minidome(request):
    """
    publicly decided ranking between two stories
    First story is random from all stories
    second story is random from those with fewer test than first story
    """
    if request.method == "POST":
        if request.user.is_authenticated:
            form = MiniDomeLoggedInForm(request.POST or None)
        else:
            form = MiniDomePublicForm(request.POST or None)

        if form.is_valid():
            #first we update the minidome
            form_uncommitted = form.save(commit = False)
            stories_options = request.session["minidome_stories"]
            loser = stories_options.remove(request.winner)
            form_uncommitted.loser = loser
            form_uncommitted.save()
            messages.success(request, 'Your judgement is final. No further corresepndance may be entered into.')
            return redirect('home')

    #check to see if user has already had stories chosen

    if request.session.get('minidome_stories', False):
        story1 = Story.objects.get(pk = request.session['minidome_stories'][0])
        story2 = Story.objects.get(pk = request.session['minidome_stories'][1])
        if request.user.is_authenticated:
            form = MiniDomeLoggedInForm( [story1.pk, story2.pk] )
        else:
            form = MiniDomePublicForm( [story1.pk, story2.pk] )
    else :
        #decide stories in match
        if request.user.is_authenticated:
            #Find lowest number of logged in matches
            min_tests = StoryStats.objects.all().aggregate(Min('minidome_total_logged_in_tests'))
            min_tests_value = min_tests['minidome_total_logged_in_tests__min']
            if min_tests_value is None:
                messages.error(request, 'Not enough stories')
                return redirect('home')

            #Create list of stories that exceed or equal lowestnumber of matches
            stories1 = list(Story.objects.filter(access__gte=1).filter(stats__minidome_total_logged_in_tests__gt=min_tests_value))

            #redo it if there are none (no matches so far or everyone is equal for some reason)
            if len(stories1) == 0 :
                stories1 = list(Story.objects.filter(access__gte=1).filter(stats__minidome_total_logged_in_tests__gte=min_tests_value))
                if len(stories1) <= 1 : #because that's itself
                    messages.error(request, 'Not enough stories')
                    return redirect('home')

                stories = sample(stories1, 2)
                story1 = stories[0]
                story2 = stories[1]

            else:

                #Get number of matches of story and then choose from list of stories that have same or less.
                story1 = sample(stories1, 1)
                story1_stats = StoryStats.objects.get(pk = story1)

                stories2 = list(Story.objects.filter(access__gte=1).filter(stats__minidome_total_logged_in_tests__lt = story1_stats.minidome_total_logged_in_tests))
                story2 = sample(stories2, 1)

            form = MiniDomeLoggedInForm( [story1.pk, story2.pk] )

        else:
            #find lowest number of public matches
            min_tests = StoryStats.objects.all().aggregate(Min('minidome_total_public_tests'))
            min_tests_value = min_tests['minidome_total_public_tests__min']
            if min_tests_value is None:
                messages.error(request, 'Not enough stories')
                return redirect('home')
            #Create list of stories that exceed or equal lowestnumber of matches
            stories1 = list(Story.objects.filter(access__gte=2).filter(stats__minidome_total_public_tests__gt=min_tests['minidome_total_public_tests__min']))

             #redo it if there are none (no matches so far or everyone is equal for some reason)
            if len(stories1) == 0 :
                stories1 = list(Story.objects.filter(access__gte=1).filter(stats__minidome_total_public_tests__gte=min_tests['minidome_total_public_tests__min']))
                if len(stories1) <= 1 : #because that's itself
                    messages.error(request, 'Not enough stories')
                    return redirect('home')
                stories = sample(stories1, 2)
                story1 = stories[0]
                story2 = stories[1]
            else:
                #Get number of matches of story and then choose from list of stories that have same or less.
                story1 = sample(stories1, 1)
                story1_stats = StoryStats.objects.get(pk = story1)

                stories2 = list(Story.objects.filter(access__gte=2).filter(stats__minidome_total_public_tests__lt = story1_stats.minidome_total_public_tests))
                story2 = sample(stories2, 1)

            form = MiniDomePublicForm( [story1.pk, story2.pk] )

    story1_context = story1
    story2_context = story2

    request.session['minidome_stories'] = [story1.pk, story2.pk]

    return render(request, 'universal/minidome.html', {
        'story2_context' : story2_context,
        'story1_context' : story1_context,
        'form': form,
        }
    )
