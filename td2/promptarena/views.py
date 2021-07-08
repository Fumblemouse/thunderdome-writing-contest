"""List of views"""
# import the logging library
import logging

from django.utils import timezone


#from django.http import HttpResponseRedirect
#from django.core.exceptions import ValidationError

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


from baseapp.models import Story
from baseapp.utils import HTML_wordcount

from .forms import (
    ContestStoryForm,
    CreateContestForm,
    #CopyContestForm,
    EnterContestNewStoryForm,
    EnterContestOldStoryForm,
    EnterCritForm,
    AddJudgeForm,
    )
from .models import  Contest, Crit, Entry


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


@login_required
def create_contest(request):
    """User creates a new contest"""
    #context = {}
    contest_form = CreateContestForm(request.POST or None)
    if  contest_form.is_valid():

        #save w/o comitting then save
        contest_form_uncommitted = contest_form.save(commit=False)
        contest_form_uncommitted.creator = request.user
        contest_form_uncommitted.save()
        messages.success(request, 'Your contest was submitted successfully! Hopefully it doesn\'t suck.')
        return redirect('view contests')

    return render(request, "promptarena/create-contest.html", {'form': contest_form})

@login_required
def edit_contest(request, contest_id = ""):
    """User edits an existing contest"""
    #context = {}
    # get the story to update
    contest = get_object_or_404(Contest, pk = contest_id)
    if request.user != contest.creator:
        messages.error(request, "Only the creator can edit their own contests.")
        return redirect('view contests')
    if contest.is_active():
        messages.error(request, "Your contest is already live.  It cannot be edited at this time.")
        return redirect('view contest details', contest_id = contest.pk)

    contest_form = CreateContestForm(request.POST or None, instance = contest)
    if  contest_form.is_valid():

        #save w/o comitting then save
        contest_form_uncommitted = contest_form.save(commit=False)
        contest_form_uncommitted.creator = request.user
        contest_form_uncommitted.save()
        messages.success(request, 'Your contest was updated successfully! Hopefully you haven\'t confused everybody.')
        return redirect('view contests')

    return render(request, "promptarena/create-contest.html", {'form': contest_form})

@login_required
def add_judge(request, contest_id = ""):
    """Adding a judge to a contest"""
    contest_context = get_object_or_404(Contest, pk = contest_id)
    if request.user != contest_context.creator:
        messages.error(request, "Only the creator can add judges to the contest.")
        return redirect('view contests')
    if contest_context.status == Contest.CLOSED:
        messages.error(request, "Contest is already closed. That ship has sailed, buddy.")
        return redirect('view contest details', contest_id = contest_context.pk)
    judge_form = AddJudgeForm(request.POST or None,
        contest_id = contest_id,)
    if judge_form.is_valid():
        judge_form_uncommitted = judge_form.save(commit = False)
        judge_form_uncommitted.contest = contest_context
        judge_form_uncommitted.save()
        messages.success(request, 'You have added a judge!')

    return render(request, "promptarena/add-judge.html", {'form': judge_form})


@login_required
def confirm_enter_contest(request, contest_id,):
    contest_context = get_object_or_404(Contest, pk=contest_id)
    if request.method == "POST":


@login_required
def enter_contest_new_story(request, contest_id,):
    """User enters new story"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    story_form = ContestStoryForm(request.POST or None)
    if request.method == "POST":
        if contest_context.status != Contest.OPEN:
            messages.error(request, 'This contest is not currently open for new entries.')
            #return with fields filled so work isn't lost
            return render(request, 'promptarena/enter-contest-new-story.html', {
                    'contest_context' : contest_context,
                    #'entry_form': entry_form,
                    'story_form' : story_form,
                    }
            )
        if story_form.is_valid():
            story_wordcount = HTML_wordcount(story_form.instance.content)
            entry_form = EnterContestNewStoryForm(
                request.POST,
                contest_max_wordcount=contest_context.max_wordcount,
                story_wordcount=story_wordcount,
                contest_expiry_date=contest_context.expiry_date,
            )
            if entry_form.is_valid():
                #add user to story
                story_form_uncommitted = story_form.save(commit=False)
                story_form_uncommitted.author = request.user

                #add contest and snapshot of story (title and content) to entry
                entry_form_uncommitted = entry_form.save(commit = False)
                entry_form_uncommitted.story = story_form_uncommitted
                entry_form_uncommitted.title = story_form_uncommitted.title
                entry_form_uncommitted.content = story_form_uncommitted.content
                entry_form_uncommitted.contest = contest_context

                story_form_uncommitted.save()
                entry_form_uncommitted.save()

                messages.success(request, 'Your entry was added to your stories list and submitted successfully! Hopefully it doesn\'t suck.')
                return redirect('view contests')

        #return with fields filled so work isn't lost
        return render(request, 'promptarena/enter-contest-new-story.html', {
            'contest_context' : contest_context,
        #    'entry_form': entry_form,
            'story_form' : story_form,
            }
        )

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
        if contest_context.status != Contest.OPEN:
            messages.error(request, 'This contest is not currently open for new entries.')
            return redirect('view contests')
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
            entry_form_uncommitted.title = chosen_story.title
            entry_form_uncommitted.content = chosen_story.content
            entry_form_uncommitted.save()

            messages.success(request, 'Your entry was submitted successfully! Hopefully it doesn\'t suck.')
            return redirect('view contests')
        messages.error(request, 'Something went wrong')
        return render(request, 'promptarena/enter-contest-old-story.html', {
            'contest_context' : contest_context,
            'entry_form': entry_form,
            }
        )

    story_context = Story.objects.filter(
        author = request.user,
        has_been_public = False
    )

    return render(request, 'promptarena/enter-contest-old-story.html', {
        'contest_context' : contest_context,
        'story_context' : story_context,
        }
    )


###These are for opening, closing and judging contests by 'hand' rather than programmatic methods
#as such theey are not long for this world.
#as we now have scheduling


@login_required
def open_contest(request, contest_id):
    """User closes specific contest """
    contest_context = get_object_or_404(Contest, pk=contest_id)
    context = {
        'contest_context' : contest_context,
    }
    if contest_context.status == Contest.OPEN:
        messages.error(request, "It's already open")
        return render(request, 'promptarena/view-contest-details.html', context)
    contest_context.open()
    messages.success(request, 'You have successfully opened the contest')
    return render(request, 'promptarena/view-contest-details.html', context)

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
def judge_contest(request, contest_id = 0):
    """Let they that have understanding count the number of the crits"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    context = {
        'contest_context' : contest_context,
    }
    if contest_context.status != Contest.JUDGEMENT:
        messages.error(request, 'You cannot judge a contest that is not ready for judgement')
        return render(request, 'promptarena/view-contest-details.html', context)
    contest_context.judge()
    messages.success(request, 'You have successfully judged the contest')
    context['entry_context'] = Entry.objects.filter(contest=contest_id).order_by('position')
    return render(request, 'promptarena/view-contest-judgement.html', context)

### Back to actual views

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
        status = Contest.CLOSED
    )

    old_contest_list = Contest.objects.filter (
         status = Contest.CLOSED
    )

    context = {
        'current_contest_list': current_contest_list,
        'old_contest_list': old_contest_list,
    }
    return render(request, 'promptarena/view-contests.html', context)

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
                return redirect('judgemode')



    crit_list = Crit.objects.filter(
        reviewer = request.user,
        entry__contest__status = Contest.JUDGEMENT
        ).order_by('final')
    context = {
        'crit_list': crit_list
    }
    if crit:
        context['form'] = crit_form
        context['crit_context'] = crit
    return render(request, 'promptarena/judgemode.html', context)



def view_contest_judgement(request, contest_id = 0):
    """Let they that have understanding count the number of the crits"""
    contest_context = get_object_or_404(Contest, pk=contest_id)
    context = {
        'contest_context' : contest_context,
    }
    context['entry_context'] = Entry.objects.filter(contest=contest_id).order_by('position')
    return render(request, 'promptarena/view-contest-judgement.html', context)
