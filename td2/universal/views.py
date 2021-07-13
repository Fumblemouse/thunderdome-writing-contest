""""
Views for public (non-logged-in functionality)
"""

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from random import sample

from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.contrib import messages
from django.db.models import Min, F


from baseapp.utils import (
    set_expirable_var,
    get_expirable_var,
    get_expirable_var_time_to_del,
)

from baseapp.models import Story, StoryStats

from .models import MiniDome
from .forms import MiniDomePublicForm, MiniDomeLoggedInForm



# Create your views here.

def get_min_tests_value(logged_in):

    if logged_in:
        wins_str = "minidome_logged_in_wins"
        losses_str = "minidome_logged_in_losses"
    else:
        wins_str = "minidome_public_wins"
        losses_str = "minidome_public_losses"

    min_tests = StoryStats.objects.all().aggregate(
            min_tests=Min(F(wins_str) + F(losses_str))
        )
    min_tests_value = min_tests["min_tests"]

    return min_tests_value

def get_story_list(logged_in, min_tests_value = 0, max_tests_value = 0):
    if logged_in:
        wins_str = "stats__minidome_logged_in_wins"
        losses_str = "stats__minidome_logged_in_losses"
        min_access = MiniDome.LOGGED_IN
    else:
        wins_str = "stats__minidome_public_wins"
        losses_str = "stats__minidome_public_losses"
        min_access = MiniDome.PUBLIC

    if  min_tests_value:
        return list(
            Story.objects.filter(access__gte = min_access)
            .annotate(
                total_logged_in_tests=F(wins_str)
                + F(losses_str)
            )
            .exclude(total_logged_in_tests__lte = min_tests_value)
        )

    elif max_tests_value:
        return list(
            Story.objects.filter(access__gte = min_access)
            .annotate(
                total_logged_in_tests=F(wins_str)
                + F(losses_str)
            )
            .exclude(total_logged_in_tests__gte = max_tests_value)
        )
    else:
        return list(
            Story.objects.filter(access__gte = min_access)
            .annotate(
                total_logged_in_tests=F(wins_str)
                + F(losses_str)
            )
        )

def get_story_stats(story_stats, logged_in):
    if logged_in:
        return story_stats.get_minidome_total_logged_in_tests()
    else:
        return story_stats.get_minidome_total_public_tests()

def get_minidome_form(logged_in, story1, story2):
    if logged_in:
        return MiniDomeLoggedInForm([story1.pk, story2.pk])
    else:
        return MiniDomePublicForm([story1.pk, story2.pk])


def set_minidome_stories(request, logged_in, min_tests_value):

    # Create list of stories that exceed or equal lowestnumber of matches
    stories1 = get_story_list(logged_in, min_tests_value = min_tests_value)
    # redo it if there are none (no matches so far or everyone is equal for some reason)
    if len(stories1) == 0:
        get_story_list(logged_in)

        if len(stories1) <= 1:  # because that's itself
            return "Not enough stories1"
        else:
            stories = sample(stories1, 2)
            story1 = stories[0]
            story2 = stories[1]
    else:
        # Get number of matches of story and then choose from list of stories that have same or less.
        story1 = sample(stories1, 1)[0]
        story1_stats = StoryStats.objects.get(pk=story1)
        story1_total_tests = get_story_stats(story1_stats, logged_in)

        stories2 = get_story_list(logged_in, max_tests_value = story1_total_tests)

        if len(stories2) == 0:
            stories2 = get_story_list(logged_in, max_tests_value = story1_total_tests + 1).remove(story1)
            if len(stories2) == 0:
                return "Not enough stories2"

        story2 = sample(stories2, 1)[0]
        form = get_minidome_form(logged_in, story1, story2)

    return [story1, story2, form]




def minidome(request):
    """
    publicly decided ranking between two stories
    First story is random from all stories
    second story is random from those with fewer test than first story
    Process:
        test if already judged (redirect if have)
        Use existing stories if session vars set (prevents gaming system)
        If no stories in session vars, set stories
        choose and deliver form
    """

    #First test to make sure they haven't judged recently (prevent spam)
    if get_expirable_var(request.session, "minidome_judged", None):
        ttl = get_expirable_var_time_to_del(request.session, "minidome_judged")
        messages.error(
            request,
            "Go home, judge, you're drunk with power. Time until sobriety: "
            + str(int(ttl))
            + " seconds",
        )
        return redirect("home")


    logged_in = request.user.is_authenticated


    #next check the values in the session variable
    story_ids = get_expirable_var(request.session, "minidome_stories", None)
    if story_ids is not None:
        story1 = Story.objects.get(pk=story_ids[0])
        story2 = Story.objects.get(pk=story_ids[1])
        stories_options = [story1, story2]

        if logged_in:
            form = MiniDomeLoggedInForm( [story1.pk, story2.pk], request.POST or None )

        else:
            form = MiniDomePublicForm( [story1.pk, story2.pk], request.POST or None )

    if request.method == "POST" and form.is_valid():
            #first we update the minidome
        form_uncommitted = form.save(commit=False)
        winner = form.cleaned_data.get("winner")
        stories_options.remove(winner)
        form_uncommitted.loser = stories_options[0]
        form_uncommitted.category = MiniDome.LOGGED_IN if logged_in else MiniDome.PUBLIC
        form_uncommitted.save()
        expire_at = datetime.today() + timedelta(minutes=30)
        set_expirable_var(request.session, "minidome_judged", True, expire_at)
        messages.success(
            request,
            "Your judgement is final. No further correspondance may be entered into.",
        )
        return redirect("home")

    min_tests_value = get_min_tests_value(logged_in)
    if min_tests_value is None:
        messages.error(request, "Not enough stories")
        return redirect("home")

    else:
        stories = set_minidome_stories(request, logged_in, min_tests_value)
        if type(stories) == str:
            messages.error(request, stories)
            return redirect("home")


    story1_context = stories[0]
    story2_context = stories[1]
    form = stories[2]

    expire_at = datetime.today() + timedelta(minutes=30)
    set_expirable_var(
        request.session, "minidome_stories", [story1_context.pk, story2_context.pk], expire_at
    )

    return render(
        request,
        "universal/minidome.html",
        {
            "story2_context": story2_context,
            "story1_context": story1_context,
            "form": form,
        },
    )
