"""List of views"""
# import the logging library
import logging

from django.utils import timezone


#from django.http import HttpResponseRedirect
#from django.core.exceptions import ValidationError

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from baseapp.forms import StoryForm
from baseapp.models import Story
from baseapp.utils import HTML_wordcount

from .forms import (
    PromptForm,
    CreateContestNewPromptForm,
    CreateContestOldPromptForm,
    EnterContestNewStoryForm,
    EnterContestOldStoryForm,
    EnterCritForm,)
from .models import Prompt, Contest, Crit, Entry


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

@login_required
def create_prompt(request):
    """User enters new prompt"""
    context ={}
    #create object for form
    form = PromptForm(request.POST or None)
     # check if form data is valid
    if form.is_valid():
        # save the form data to model
        form_uncommitted = form.save(commit=False)
        form_uncommitted.creator = request.user
        form_uncommitted.save()
        messages.success(request, 'Your prompt was submitted successfully! Hopefully it doesn\'t suck.')
        return redirect('view prompt details', prompt_id = form_uncommitted.pk)
    context['form'] = form
    return render(request, "promptarena/create-prompt.html", context)

@login_required
def edit_prompt(request, prompt_id = 0):
    """update a prompt"""
    # get the story to update
    prompt = get_object_or_404(Prompt, pk = prompt_id)
    contests = Contest.objects.filter(prompt = prompt_id)
    for contest in contests:
        if contest.status != 'UNOPENED' or 'CLOSED':
            messages.error(request, "Your prompt is currently being used in a contest.  It cannot be edited at this time.")
            return redirect('view prompt details', prompt_id = prompt_id)
    # create a form instance and populate it with data from the request or the :
    form = PromptForm(request.POST or None, instance = prompt)
    # check whether it's valid:
    if form.is_valid():
        form.save()
        messages.success(request, 'Your prompt was updated successfully! Hopefully it doesn\'t suck.')
        # redirect to a new URL:
        return redirect('view prompt details', prompt_id = prompt.pk)

    return render(request, 'promptarena/create-prompt.html', {'form': form})


@login_required
def create_contest_new_prompt(request):
    """User enters new contest with a new prompt"""
    #context = {}
    prompt_form = PromptForm(request.POST or None)
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
        return redirect('view contests')

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
        return redirect('view contests')
    return render(request, "promptarena/create-contest-old-prompt.html", {'form': form})



@login_required
def enter_contest_new_story(request, contest_id,):
    """User enters new story"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    story_form = StoryForm(request.POST or None)
    if request.method == "POST":
        if story_form.is_valid():
            story_wordcount = HTML_wordcount(story_form.instance.content)
            entry_form = EnterContestNewStoryForm(
                request.POST,
                contest_max_wordcount=contest_context.wordcount,
                story_wordcount=story_wordcount,
                contest_expiry_date=contest_context.expiry_date,
            )
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
                return redirect('view contest')
        return render(request, 'promptarena/enter-contest-new-story.html', {
            'contest_context' : contest_context,
            'entry_form': entry_form,
            'story_form' : story_form,
            }
        )
    if contest_context.status != 'OPEN':
        messages.error(request, 'This contest is not currently open for new entries.')
        return render(request, 'promptarena/view-contests.html', {})


    return render(request, 'promptarena/enter-contest-new-story.html', {
        'contest_context' : contest_context,
        #'entry_form': entry_form or None,
        'story_form' : story_form,
        }
    )

@login_required
def enter_contest_old_story(request, contest_id,):
    """User enters new story from a list of their own non-public stories"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    if request.method == "POST":
        chosen_story = get_object_or_404(Story, pk=request.POST.get('story'))
        entry_form = EnterContestOldStoryForm(request.POST,
            contest_expiry_date =  contest_context.expiry_date,
            contest_max_wordcount=contest_context.max_wordcount,
            story_wordcount=chosen_story.wordcount,
        )
        if entry_form.is_valid():
            #add contest to entry
            entry_form_uncommitted = entry_form.save(commit = False)
            entry_form_uncommitted.contest = contest_context

            entry_form_uncommitted.save()

            messages.success(request, 'Your entry was submitted successfully! Hopefully it doesn\'t suck.')
            return redirect('view contests')
        messages.error(request, 'Something went wrong')
        return render(request, 'promptarena/enter-contest-old-story.html', {
            'contest_context' : contest_context,
            'entry_form': entry_form,
            }
        )
    if contest_context.status != 'OPEN':
        messages.error(request, 'This contest is not currently open for new entries.')
        return render(request, 'promptarena/view-contests.html', {})

    story_context = Story.objects.filter(
        author = request.user,
        has_been_public = False
    )

    return render(request, 'promptarena/enter-contest-old-story.html', {
        'contest_context' : contest_context,
        'story_context' : story_context,
        #'entry_form': entry_form or None,
        }
    )




@login_required
def close_contest(request, contest_id):
    """User closes specific contest """
    contest_context = get_object_or_404(Contest, pk=contest_id)
    context = {
        'contest_context' : contest_context,
    }
    if contest_context.status != 'OPEN':
        messages.error(request, 'You cannot close a contest that is not open')
        return render(request, 'promptarena/view-contest-details.html', context)
    contest_context.close()
    messages.success(request, 'You have successfully closed the contest')
    return render(request, 'promptarena/view-contest-details.html', context)

@login_required
def open_contest(request, contest_id):
    """User closes specific contest """
    contest_context = get_object_or_404(Contest, pk=contest_id)
    context = {
        'contest_context' : contest_context,
    }
    if contest_context.status == 'OPEN':
        messages.error(request, "It's already open")
        return render(request, 'promptarena/view-contest-details.html', context)
    contest_context.open()
    messages.success(request, 'You have successfully opened the contest')
    return render(request, 'promptarena/view-contest-details.html', context)

def view_contest_details(request, contest_id):
    """User views specific prompt and metadata"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    context = {
        'contest_context' : contest_context,
    }
    return render(request, 'promptarena/view-contest-details.html', context)



def view_contests(request):
    """User views available contests"""
    current_contest_list = Contest.objects.filter (
        expiry_date__gte = timezone.now()
    ).exclude(
        status = 'CLOSED'
    )

    old_contest_list = Contest.objects.filter (
         status = 'CLOSED'
    )

    context = {
        'current_contest_list': current_contest_list,
        'old_contest_list': old_contest_list,
    }
    return render(request, 'promptarena/view-contests.html', context)



def view_prompts(request):
    """view all prompts in a list"""
    prompts_context = Prompt.objects.all
    context = {
        'prompts_context': prompts_context,
    }
    return render(request, 'promptarena/view-prompts.html', context)

def view_prompt_details(request, prompt_id=""):
    """User views specific prompt and metadata"""
    prompt_context = get_object_or_404(Prompt, pk=prompt_id)
    context = {
        'prompt_context' : prompt_context,
    }
    return render(request, 'promptarena/view-prompt-details.html', context)

@login_required
def judgemode(request, crit_id = 0):
    """Judge the supplicants mercilessly"""
    crit = {}
    if crit_id:
        crit = Crit.objects.get(
                pk = crit_id,
        )
    if crit:
        crit_form = EnterCritForm(request.POST or None, instance = crit)
    else:
        crit_form = EnterCritForm(request.POST or None)
    if request.method == "POST":
        if crit_form.is_valid():
            #check that this rating has not been used before
            used_scores = Crit.objects.filter(
                entry__contest = crit.entry.contest,
                reviewer = crit.reviewer,
                score = crit.score,
            ).exclude(
                pk = crit.pk,
            )
            if used_scores:
                messages.error(request, "You have already used that rank in this contest. Each rank given to an entry must be different.")
            else:
                #check wordcount not too little
                crit_wordcount = HTML_wordcount(crit_form.instance.content)
                crit_form_uncommitted = crit_form.save(commit=False)
                crit_form_uncommitted.wordcount = crit_wordcount
                crit_form_uncommitted.reviewer = request.user
                crit_form_uncommitted.save()
                messages.success(request, 'You have successfully critted a contest entry')

    crit_list = Crit.objects.filter(
        reviewer = request.user,
        entry__contest__status = 'JUDGEMENT'
        ).order_by('final')
    context = {
        'crit_list': crit_list
    }
    if crit:
        context['form'] = crit_form
        context['crit_context'] = crit
    return render(request, 'promptarena/judgemode.html', context)




@login_required
def judge_contest(request, contest_id = 0):
    """Let they that have understanding count the number of the crits"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    context = {
        'contest_context' : contest_context,
    }
    if contest_context.status != 'JUDGEMENT':
        messages.error(request, 'You cannot judge a contest that is not ready for judgement')
        return render(request, 'promptarena/view-contest-details.html', context)
    contest_context.judge()
    messages.success(request, 'You have successfully judged the contest')
    context['entry_context'] = Entry.objects.filter(contest=contest_id).order_by('position')
    return render(request, 'promptarena/view-contest-judgement.html', context)

def view_contest_judgement(request, contest_id = 0):
    """Let they that have understanding count the number of the crits"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    context = {
        'contest_context' : contest_context,
    }
    context['entry_context'] = Entry.objects.filter(contest=contest_id).order_by('position')
    return render(request, 'promptarena/view-contest-judgement.html', context)
