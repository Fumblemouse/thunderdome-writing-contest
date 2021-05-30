""""
Views for public (non-logged-in functionality)
"""

from random import sample

from django.shortcuts import render

from baseapp.models import Story, StoryStats
from .models import MiniDome
from .forms import MiniDomePublicForm, MiniDomeLoggedInForm





# Create your views here.

def minidome(request):
    """
    publicly decided ranking between two stories
    First story is random from all stories
    second story is random from those with fewer test than first story
    """
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
        #Then we update the story stats
        stats_winner = StoryStats.objects.get(pk = request.winner)
        stats_loser = StoryStats.objects.get(pk = request.loser)



    #first select a random story
    #access depends on if user logged in or not

    if request.user.is_authenticated:
        stories = list(Story.objects.filter(access__gte=1))
    else:
        stories = list(Story.objects.filter(access__gte=2))
    story1 = sample(stories, 1)
    story1_stats = StoryStats.objects.get(pk = story1)
    if request.user.is_authenticated:
        current_low = story1_stats.minidome_total_logged_in_tests
    else:
        current_low = story1_stats.minidome_total_public_tests
    story2 = story1

    #make sure story 2 != story 1 and story 1 has >= the number of tests
    while story2 == story1:
        potential_stories = sample(stories, 10)
        for potential_story in potential_stories:
            potential_story_stats = StoryStats.objects.get(pk = potential_story)
            if request.user.is_authenticated:
                potential_low = potential_story_stats.minidome_total_logged_in_tests
            else:
                potential_low = potential_story_stats.minidome_total_public_tests
            if potential_low <= current_low:
                story2 = potential_story

    story1_context = Story.objects.get(pk = story1)
    story2_context = Story.objects.get(pk = story2)

    request.session['minidome_stories'] = [story1, story2]

    return render(request, 'universal/minidome.html', {
        'story2_context' : story2_context,
        'story1_context' : story1_context,
        }
    )
