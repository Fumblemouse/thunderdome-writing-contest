"""views for baseapp"""
from django.shortcuts import render

"""List of views"""
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import CreateStoryForm


# Create your views here.
def home(request):
    """Homepage"""
    return render(request, 'baseapp/home.html', {})

@login_required
def create_story(request):
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
        form = CreateStory()

    return render(request, 'baseapp/create-story.html', {'form': form})
