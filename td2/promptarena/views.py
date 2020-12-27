"""List of views"""
from datetime import date
# import the logging library
import logging
import re
from django.http import HttpResponse, HttpResponseRedirect
#from django.core.exceptions import ValidationError

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import strip_tags

from baseapp.forms import CreateStoryForm
from .forms import CreatePromptForm, CreateContestNewPromptForm, CreateContestOldPromptForm, EnterContestNewStoryForm

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
    prompt_form = CreatePromptForm(request.POST or None)
    contest_form = CreateContestNewPromptForm(request.POST or None)
    if prompt_form.is_valid() and contest_form.is_valid():
        #save w/o comitting then add user and save
        prompt_form_uncommitted = prompt_form.save(commit=False)
        prompt_form_uncommitted.creator = request.user
        prompt_form_uncommitted.save()

        #save w/o comitting then add prompt and save
        contest_form_uncommitted = contest_form.save(commit=False)
        contest_form_uncommitted.prompt = prompt_form_uncommitted
        contest_form_uncommitted.save()
        messages.success(request, 'Your contest was submitted successfully! Hopefully it doesn\'t suck.')
        return HttpResponseRedirect('/')

    return render(request, "promptarena/create-contest-new-prompt.html", {'prompt_form': prompt_form, 'contest_form': contest_form})

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
def enter_contest(request, contest_id,):
    """User enters new story"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    story_form = CreateStoryForm(request.POST or None)
    #entry_form = EnterContestNewStoryForm(request.POST or None)


    if request.method == "POST":
        if story_form.is_valid(): 
            words_to_count = strip_tags(story_form.instance.content)
            story_wordcount = len(re.findall(r'\S+', words_to_count))

            entry_form = EnterContestNewStoryForm(
                request.POST,
                contest_wordcount=contest_context.wordcount,
                story_wordcount=story_wordcount
            )
            logger.error(str(contest_context.wordcount) + " : " + str(story_wordcount) )
            if entry_form.is_valid():
                #add user to story
                story_form_uncommitted = story_form.save(commit=False)
                story_form_uncommitted.author = request.user

                #add contest to entry
                entry_form_uncommitted = entry_form.save(commit = False)
                entry_form_uncommitted.story = story_form_uncommitted
                entry_form_uncommitted.contest = contest_context

                story_form_uncommitted.save()
                entry_form_uncommitted.save()

                messages.success(request, 'Your entry was submitted successfully! Hopefully it doesn\'t suck.')
                return HttpResponseRedirect('/')
        return render(request, 'promptarena/enter-contest.html', {
            'contest_context' : contest_context,
            'entry_form': entry_form,
            'story_form' : story_form,
            }
        )

        

    return render(request, 'promptarena/enter-contest.html', {
        'contest_context' : contest_context,
        #'entry_form': entry_form or None,
        'story_form' : story_form,
        }
    )





def view_full_contest(request, contest_id):
    """User views specific prompt and metadata"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    context = {
        'contest_context' : contest_context,
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
