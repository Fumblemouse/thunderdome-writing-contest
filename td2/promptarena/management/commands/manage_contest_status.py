from django.core.management.base import BaseCommand, CommandError
from django.db import connection
import time
from django.utils import timezone
from promptarena.models import Contest, Crit
from universal.models import Notification

class Command(BaseCommand):
    help = 'Sort out what contests need to do what and when (eg opening, closing, judging etc)'

    def handle(self, *args, **kwargs):
        while True:
            contests = Contest.objects.exclude(status="CLOSED")
            for contest in contests:
                category = ""
                if contest.status == contest.UNOPENED and contest.start_date < timezone.now():
                    contest.status = contest.OPEN
                    contest.save()
                    #set the category for subsequent notification if appropriate
                    if contest.mode == contest.INTERNAL_JUDGE_CONTEST:
                        category = Notification.CONTEST_ANNOUNCE_INTERNAL_JUDGE
                    elif contest.mode == contest.EXTERNAL_JUDGE_CONTEST:
                        category = Notification.CONTEST_ANNOUNCE_EXTERNAL_JUDGE
                    else:
                        category = contest.SYSTEM

                if contest.status == contest.OPEN and contest.expiry_date < timezone.now():
                    contest.close()
                    #set the category for subsequent notification if appropriate
                    if contest.mode == contest.INTERNAL_JUDGE_CONTEST:
                        category = Notification.CONTEST_CLOSE_INTERNAL_JUDGE
                    elif contest.mode == contest.EXTERNAL_JUDGE_CONTEST:
                        category = Notification.CONTEST_CLOSE_EXTERNAL_JUDGE
                    elif contest.mode == contest.BRAWL:
                        category = contest.BRAWL_CLOSE
                    else:
                        category = contest.SYSTEM

                if contest.status == contest.JUDGEMENT:
                    crit_num = Crit.objects.filter(entry__contest = contest).count()
                    if crit_num >= 3*contest.entrant_num:
                        contest.judge()
                #Create the notifcations
                if category:
                    Notification.objects.create(contest = contest, category = category)
            #we close the connection otherwise mySQL errors out after a big nap and fills the error log.
            connection.close()
            time.sleep(60*5)