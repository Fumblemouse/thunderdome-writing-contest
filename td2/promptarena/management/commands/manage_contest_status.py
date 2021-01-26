from django.core.management.base import BaseCommand, CommandError
from django.db import connection
import time
from django.utils import timezone
from promptarena.models import InternalJudgeContest, Crit

class Command(BaseCommand):
    help = 'Sort out what contests need to do what and when (eg opening, closing, judging etc)'

    def handle(self, *args, **kwargs):
        while True:
            contests = InternalJudgeContest.objects.exclude(status="CLOSED")
            for contest in contests:
                if contest.status == "UNOPENED" and contest.start_date < timezone.now():
                    contest.status = "OPEN"
                    contest.save()
                if contest.status == "OPEN" and contest.expiry_date < timezone.now():
                    contest.close()
                if contest.status == "JUDGEMENT":
                    crit_num = Crit.objects.filter(entry__contest = contest).count()
                    if crit_num >= 3*contest.entrant_num:
                        contest.judge()
            #we close the connection otherwise mySQL errors out after a big nap and fills the error log.
            connection.close()
            time.sleep(60*5)