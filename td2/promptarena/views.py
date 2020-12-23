"""List of views"""
from datetime import date
# import the logging library
import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import strip_tags
import re

from .forms import CreatePromptForm, CreateContestNewPromptForm, CreateContestOldPromptForm
from baseapp.forms import CreateStoryForm
from .models import Prompt, Contest



# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

@login_required
def create_prompt(request):
    """User enters new prompt"""
    context ={}
    #create object for form
    form = CreatePromptForm(request.POST or None)
     # check if form data is valid
    if form.is_valid():
        # save the form data to model
        form_uncommitted = form.save(commit=False)
        form_uncommitted.creator = request.user
        form_uncommitted.save()
        messages.success(request, 'Your prompt was submitted successfully! Hopefully it doesn\'t suck.')
    context['form'] = form
    return render(request, "promptarena/create-prompt.html", context)

@login_required
def create_contest_new_prompt(request):
    """User enters new contest with a new prompt"""
    #context = {}
    p_form = CreatePromptForm(request.POST or None)
    c_form = CreateContestNewPromptForm(request.POST or None)
    if p_form.is_valid() and c_form.is_valid():
        #save w/o comitting then add user and save
        p_form_uncommitted = p_form.save(commit=False)
        p_form_uncommitted.creator = request.user
        p_form_saved = p_form_uncommitted.save()

        #save w/o comitting then add prompt and save
        c_form_uncommitted = c_form.save(commit=False)
        c_form_uncommitted.prompt = p_form_uncommitted
        c_form_uncommitted.save()
        messages.success(request, 'Your contest was submitted successfully! Hopefully it doesn\'t suck.')
        return HttpResponseRedirect('/')

    return render(request, "promptarena/create-contest-new-prompt.html", {'p_form': p_form, 'c_form': c_form})

@login_required
def create_contest_old_prompt(request):
    """User enters new contest re-using a prompt"""
    #context = {}
    form = CreateContestOldPromptForm(request.POST or None)
    if form.is_valid():
        form.save(commit=False)

        form.save()
        messages.success(request, 'Your contest was submitted successfully! Hopefully it doesn\'t suck.')

    return render(request, "promptarena/create-contest-old-prompt.html", {'form': form})



@login_required
def enter_contest(request, contest_id):
    """User enters new story"""
    view_full_contest_context = get_object_or_404(Contest, pk=contest_id)
    form = EnterContestNewStoryForm(request.POST or None)
    words_to_count = strip_tags(form.content)
    wordcount = len(re.findall(r'\w+', words_to_count))


    if form.is_valid():
        form_uncommitted = form.save(commit=False)
        if form_uncommitted.story.wordcount


    return HttpResponse(response % contest_id)

def view_full_contest(request, contest_id):
    """User views specific prompt and metadata"""
    view_full_contest_context = get_object_or_404(Contest, pk=contest_id)
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

    context = {
        'current_contest_list': current_contest_list,
    }
    return render(request, 'promptarena/view-current-contests.html', context)

def view_prompts(request):
    """view all prompts in a list"""
    prompt_list = Prompt.objects.all
    context = {
        'prompt_list': prompt_list,
    }
    return render(request, 'promptarena/view-prompts.html', context)
