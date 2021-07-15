""""
Views for public (non-logged-in functionality)
"""


from random import sample

from datetime import datetime, timedelta

# import the logging library
import logging

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


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


def get_min_tests_value(logged_in):
    """GEts the lowest number of completed tests

    Args:
        logged_in (Boolean): Whether user is logged in

    Returns:
        Int: lowest number of completed tests
    """
    if logged_in:
        wins_str = "minidome_logged_in_wins"
        losses_str = "minidome_logged_in_losses"
    else:
        wins_str = "minidome_public_wins"
        losses_str = "minidome_public_losses"

    min_tests = StoryStats.objects.all().aggregate(
        min_tests=Min(F(wins_str) + F(losses_str))
    )
    return min_tests["min_tests"]


def get_story_list(request, logged_in, min_tests_value=None, max_tests_value=None):
    """Gets list of stories that

    Args:
        logged_in (Boolean): USer logged in or public
        min_tests_value (int, optional): Lowest number of tests. Defaults to 0.
        max_tests_value (int, optional): Highest number of tests. Defaults to 0.

    Returns:
        List: List of stories (recordset in list context)
    """
    if logged_in:
        wins_str = "stats__minidome_logged_in_wins"
        losses_str = "stats__minidome_logged_in_losses"
        min_access = MiniDome.LOGGED_IN
    else:
        wins_str = "stats__minidome_public_wins"
        losses_str = "stats__minidome_public_losses"
        min_access = MiniDome.PUBLIC

    query = Story.objects.filter(access__gte=min_access)
    if logged_in:
        query = query.exclude(author = request.user)


    if isinstance(min_tests_value, int):
        return list(
            query
            .annotate(total_logged_in_tests=F(wins_str) + F(losses_str))
            .exclude(total_logged_in_tests__lte=min_tests_value)
        )

    if isinstance(max_tests_value, int):
        return list(
            query
            .annotate(total_logged_in_tests=F(wins_str) + F(losses_str))
            .exclude(total_logged_in_tests__gte=max_tests_value)
        )

    return list(
        query
    )


def get_story_total_tests(story_stats, logged_in):
    """Gets the total number of mindomes contested by a particular story

    Args:
        story_stats (StoryStats): Wins and losses for a given story
        logged_in (Boolean ): User is currently logged in

    Returns:
        int: Number of tests
    """
    if logged_in:
        return story_stats.get_minidome_total_logged_in_tests()
    else:
        return story_stats.get_minidome_total_public_tests()


def get_minidome_form(logged_in, story1, story2):
    """gets the appopriate form for the situation

    Args:
        logged_in (Boolean): Is current user logged in?
        story1 (Story): First chosen Story
        story2 (Story): Second chosen story

    Returns:
        Form: Form used to submit results
    """
    if logged_in:
        return MiniDomeLoggedInForm([story1.pk, story2.pk])
    else:
        return MiniDomePublicForm([story1.pk, story2.pk])


def set_minidome_stories(request, logged_in, min_tests_value):
    """Chooses two stories to enter the minidome
    First story is random from all stories
    Second story is semi-random from stories that have entered fewer tests


    Args:
        request (request): request made for page
        logged_in (boolean ): Is current user logged in
        min_tests_value (Int): lowest number of tests

    Returns:
        [type]: [description]
    """
    # Create list of stories that exceed or equal lowestnumber of matches
    stories1 = get_story_list(request, logged_in, min_tests_value=min_tests_value)
    # redo it if there are none (no matches so far or everyone is equal for some reason)
    if len(stories1) == 0:
        stories1 = get_story_list(request, logged_in)

        if len(stories1) <= 1:  # because that's itself
            return "Not enough stories"
        stories = sample(stories1, 2)
        story1 = stories[0]
        story2 = stories[1]
    else:
        # Get number of matches of story and then choose from list of stories that have same or less.
        story1 = sample(stories1, 1)[0]
        story1_stats = StoryStats.objects.get(pk=story1)
        story1_total_tests = get_story_total_tests(story1_stats, logged_in)
        stories2 = get_story_list(request, logged_in, max_tests_value=story1_total_tests)

        if not stories2:
            stories2 = get_story_list(
                request, logged_in, max_tests_value=story1_total_tests + 1
            )
            stories2.remove(story1)

        if not stories2:
            return "Not enough stories"

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

    # First test to make sure they haven't judged recently (prevent spam)
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
    # next check the values in the session variable
    story_ids = get_expirable_var(request.session, "minidome_stories", None)
    if story_ids is not None:
        story1 = Story.objects.get(pk=story_ids[0])
        story2 = Story.objects.get(pk=story_ids[1])
        stories_options = [story1, story2]

        if logged_in:
            form = MiniDomeLoggedInForm([story1.pk, story2.pk], request.POST or None)

        else:
            form = MiniDomePublicForm([story1.pk, story2.pk], request.POST or None)

    if request.method == "POST" and story_ids:
        if form.is_valid():
            return handle_form_submission(form, stories_options, logged_in, request)
    min_tests_value = get_min_tests_value(logged_in)
    if not isinstance(min_tests_value, int):
        messages.error(request, "Not enough stories")
        return redirect("home")

    stories = set_minidome_stories(request, logged_in, min_tests_value)
    if isinstance(stories, str):
        messages.error(request, stories)
        return redirect("home")
    story1_context = stories[0]
    story2_context = stories[1]
    form = stories[2]

    expire_at = datetime.today() + timedelta(minutes=30)
    set_expirable_var(
        request.session,
        "minidome_stories",
        [story1_context.pk, story2_context.pk],
        expire_at,
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


def handle_form_submission(form, stories_options, logged_in, request):
    """Handles the submissionof a minidome judgement by a user user

    Args:
        form (Form): Form used to submit user Judgement
        stories_options (List): List comprising the two stories being judged
        logged_in (Boolean): Is current user logged in?
        request (Request): IP request?

    Returns:
        Redirect: Once the work is done, sends user to home page.
    """
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
