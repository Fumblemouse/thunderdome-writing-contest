"""views for baseapp"""
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth import get_user_model

from .forms import CreateStoryForm
from .models import Story


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
        form = CreateStoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            form.instance.author = request.user
            form.save()
            messages.success(request, 'Your story was submitted successfully! Hopefully it doesn\'t suck.')
            # redirect to a new URL:
            return HttpResponseRedirect('create-story')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreateStoryForm()

    return render(request, 'baseapp/create-story.html', {'form': form})

def view_stories(request):
    """User retrieves a list of available stories"""
    stories_context = Story.objects.filter(
        public_view_allowed = True
    )
    
    return render(request, 'baseapp/view-stories.html', {'stories_context': stories_context})

def view_stories_by_author(request, username):
    """User retrieves a list of available stories"""
    author = get_object_or_404(get_user_model(), username=username)
    stories_context = Story.objects.filter(
        public_view_allowed = True,
        author = author,
    )
    author_context = author
    return render(request, 'baseapp/view-stories.html', {'stories_context': stories_context, 'author_context': author_context})

def view_story_by_id(request, story_id = 0):
    """User views a story"""
    story_context = get_object_or_404(Story, pk=story_id)
    return render(request, 'baseapp/view-story.html', {'story_context': story_context})

def view_story_by_slug(request, slug = ''):
    """User views a story"""
    story_context = get_object_or_404(Story, slug=slug)
    return render(request, 'baseapp/view-story.html', {'story_context': story_context})
