"""views for baseapp"""
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth import get_user_model

from .forms import StoryForm
from .models import Story
from promptarena.models import Entry, Crit
from baseapp.utils import check_story_permissions

import logging
logger = logging.getLogger(__name__)



# Create your views here.
def home(request):
    """Homepage"""
    return render(request, 'baseapp/home.html', {})

@login_required
def create_story(request):
    """create a magical story of myth and wonder"""
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = StoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.instance.author = request.user
            saved_form = form.save()
            messages.success(request, 'Your story was submitted successfully! Hopefully it doesn\'t suck.')
            # redirect to a new URL:
            return redirect('view story by id', story_id = saved_form.pk)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = StoryForm()

    return render(request, 'baseapp/create-story.html', {'form': form})

@login_required
def edit_story(request, story_id=""):
    """update a magical story of myth and wonder"""
    # get the story to update
    story = get_object_or_404(Story, pk = story_id)
    if not check_story_permissions(request, story):
        messages.error(request, "Only the author can edit their own stories.")
        return redirect('view stories')
    entries = Entry.objects.filter(story = story_id)
    for entry in entries:
        if entry.contest.status != 'UNOPENED' or 'CLOSED':
            messages.error(request, "Your story is already in a contest.  It cannot be edited at this time.")
            return redirect('view story by id', story_id = story.pk)
    # create a form instance and populate it with data from the request or the :
    form = StoryForm(request.POST or None, instance = story)
    # check whether it's valid:
    if form.is_valid():
        # process the data in form.cleaned_data as required
        form.instance.author = request.user
        form.save()
        messages.success(request, 'Your story was updated successfully! Hopefully it doesn\'t suck.')
        # redirect to a new URL:
        return redirect('view story by slug', author_slug = story.author.profile.slug, story_slug = story.slug)

    return render(request, 'baseapp/create-story.html', {'form': form})

def view_stories(request):
    """User retrieves a list of available stories"""
    if request.user.is_authenticated:
        stories_context = Story.objects.filter(
            access__gte = Story.LOGGED_IN,
            author__profile__public_profile = True,
        )
    elif request.user.is_staff:
        stories_context = Story.objects.all()
    else:
        stories_context = Story.objects.filter(
            access__gte = Story.PUBLIC,
            author__profile__public_profile = True,
        )

    return render(request, 'baseapp/view-stories.html', {'stories_context': stories_context})

def view_stories_by_author(request, author_slug =""):
    """User retrieves a list of available stories"""
    author = get_object_or_404(get_user_model(), profile__slug=author_slug)
    if request.user.is_staff:
        stories_context = Story.objects.filter(
            author = author,
        )
    elif request.user.is_authenticated:
        stories_context = Story.objects.filter(
            access__gte= 1,
            author = author,
            author__profile__public_profile = True
        )
    else:
        stories_context = Story.objects.filter(
            access__gte= 2,
            author = author,
            author__profile__public_profile = True
        )

    author_context = author
    return render(request, 'baseapp/view-stories.html', {'stories_context': stories_context, 'author_context': author_context})

@login_required
def view_story_by_id(request, story_id = 0):
    """User views a story"""
    story_context = get_object_or_404(Story, pk=story_id)
    if not check_story_permissions(request, story_context):
        messages.error(request, "This story has been locked by the author.")
        return redirect('view stories')

    return render(request, 'baseapp/view-story.html', {'story_context': story_context})

def view_story_by_slug(request, author_slug="", story_slug = ""):
    """User views a story"""
    context = {}
    context['story_context'] = get_object_or_404(Story, author__profile__slug =author_slug, slug = story_slug)
    if not check_story_permissions(request, context['story_context']):
        messages.error(request, "This story has been locked by the author.")
        return redirect('view stories')
    context['crit_context'] = Crit.objects.filter (
        story = context['story_context']
    )
    return render(request, 'baseapp/view-story.html', context)
