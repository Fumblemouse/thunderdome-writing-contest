"""List of views"""
from datetime import date
# import the logging library
import logging
from django.http import HttpResponse
from django.template import loader

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import EnterPrompt
from .models import Prompt,Contest



# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

@login_required
def enter_prompt(request):
    """User enters new prompt"""
    context ={}
    #create object for form
    form = EnterPrompt(request.POST or None)
     # check if form data is valid
    if form.is_valid():
        # save the form data to model
        form.instance.creator = request.user
        form.save()
        messages.success(request, 'Your prompt was submitted successfully! Hopefully it doesn\'t suck.')
    context['form'] = form
    return render(request, "promptarena/enter-prompt.html", context)

@login_required
def enter_contest(request):
    """User enters new contest"""
    return HttpResponse('Please enter your Contest')

@login_required
def enter_story(request, contest_id):
    """User enters new story"""
    response = "Please enter your story for contest %s."
    return HttpResponse(response % contest_id)

def view_full_contest(request, contest_id):
    """User views specific prompt and metadata"""
    view_full_contest_context = get_object_or_404(Contest, pk=contest_id)
    loader.get_template('promptarena/view-full-contest.html')
    context = {
        'view_full_contest_context' : view_full_contest_context,
    }
    return render(request, 'promptarena/view-full-contest.html', context)

def view_story(request, story_id):
    """User views a story"""
    response = "You're looking at story %s."
    return HttpResponse(response % story_id)

def view_current_contests(request):
    """User views available contests"""
    current_contest_list = Contest.objects.filter (
        expiry_date__gte = date.today()
    )

    loader.get_template('promptarena/view-current-contests.html')
    context = {
        'current_contest_list': current_contest_list,
    }
    return render(request, 'promptarena/view-current-contests.html', context)

def view_prompts(request):
    """view all prompts in a list"""
    prompt_list = Prompt.objects.all
    loader.get_template('promptarena/view-prompts.html')
    context = {
        'prompt_list': prompt_list,
    }
    return render(request, 'promptarena/view-prompts.html', context)
