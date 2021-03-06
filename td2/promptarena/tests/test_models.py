"""Test models for Stories"""
from promptarena.models import InternalJudgeContest, Brawl, Entry, Crit, Contest
from baseapp.tests.test_utils import BaseAppTestCase


class BrawlContestModelTest(BaseAppTestCase):
    """Test A Contest"""

    def setUp(self):
        """set up contest"""
        self.set_up_contest(Brawl)
        self.contest.save()

    def test_brawl_contest_close_function(self):
        """tests close function which changes status"""

        self.set_up_contest_components(num_entrants=2)
        self.contest.close()
        self.assertEqual(self.contest.status, Contest.JUDGEMENT)

    def test_brawl_close_crit_creation(self):
        """Tests empty crits get created when contest is closed"""
        self.set_up_contest_components(num_entrants=2)
        self.contest.close()
        self.assertEqual(Crit.objects.filter(entry__contest=self.contest).count(), 2)

    ###Judge tests
    def test_brawl_judge_function(self):
        """Tests function reaches end and sets contest.status"""
        self.set_up_contest_components(num_entrants=2)
        self.contest.close()
        self.score_brawl()
        self.contest.judge()
        self.assertEqual(self.contest.status, Contest.CLOSED)

    def test_brawl_judge_entrant_num(self):
        """test function reaches end and sets contest entrant_num"""
        self.set_up_contest_components(num_entrants=2)
        self.contest.close()
        self.score_brawl()
        self.contest.judge()
        self.assertTrue(self.contest.entrant_num > 0)

    def test_brawl_judge_entry_updates(self):
        """test function reaches end and handles entries and scores for entries"""
        self.set_up_contest_components(num_entrants=2)
        self.contest.close()
        self.score_brawl()
        self.contest.judge()
        for entry in self.entries:
            entry.refresh_from_db()
            self.assertTrue(entry.position > 0)
            self.assertTrue(entry.score > 0)

    def test_brawl_profile_updates(self):
        """test function reaches end and checks profiles updated with stats"""
        brawl_win = 0
        brawl_loss = 0
        self.set_up_contest_components(num_entrants=2)
        self.contest.close()
        self.score_brawl()

        self.contest.judge()
        for entry in self.entries:
            entry.refresh_from_db()
            if entry.author.brawl_wins == 1:
                brawl_win += 1
            if entry.author.brawl_losses == 1:
                brawl_loss += 1

        self.assertTrue(brawl_win)
        self.assertTrue(brawl_loss)


class InternalJudgeContestModelTest(BaseAppTestCase):
    """Test A Contest
    Because this was the first type written we use it to test a lot of
    contest based stuff too
    """

    def setUp(self):
        """set up contest"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()

    def test_contest_string_representation(self):
        """test nameing string"""
        self.assertEqual(str(self.contest), self.contest.title)

    ###Save tests
    def test_contest_save_function(self):
        """test modified save routine that creates new slug"""
        self.assertTrue(self.contest.slug == "my-contest-title")

    def test_contest_save_title_again_function(self):
        """tests modified save routine if contest title changes"""
        self.contest.title = "My changed title"
        self.contest.save()
        self.assertTrue(self.contest.slug == "my-changed-title")

    #
    def test_contest_set_status_function(self):
        """test open function which changes contest status"""
        self.contest.set_status(self.contest.OPEN)
        self.assertTrue(self.contest.status == self.contest.OPEN)

    ###Close tests
    def test_ij_contest_close_function(self):
        """tests close function which changes status"""
        self.set_up_contest_components()
        self.contest.close()
        self.assertEqual(self.contest.status, Contest.JUDGEMENT)

    def test_contest_close_crit_creation(self):
        """Tests empty crits get created when contest is closed"""
        self.set_up_contest_components()
        self.contest.close()
        self.assertEqual(Crit.objects.filter(entry__contest=self.contest).count(), 15)

    ###Judge tests
    def test_contest_judge_function(self):
        """Tests function reaches end and sets contest.status"""
        self.set_up_contest_components()
        self.contest.close()
        self.score_contest()
        self.contest.judge()
        self.assertEqual(self.contest.status, Contest.CLOSED)

    def test_contest_judge_entrant_num(self):
        """test function reaches end and sets contest entrant_num"""
        self.set_up_contest_components()
        self.contest.close()
        self.score_contest()
        self.contest.judge()
        self.assertTrue(self.contest.entrant_num > 0)

    def test_contest_judge_entry_updates(self):
        """test function reaches end and handles entries and scores for entries"""
        self.set_up_contest_components()
        self.contest.close()
        self.score_contest()
        self.contest.judge()
        for entry in self.entries:
            entry.refresh_from_db()
            self.assertTrue(entry.position > 0)
            self.assertTrue(entry.score > 0)

    def test_contest_profile_updates(self):
        """test function reaches end and checks profiles updated with stats"""
        win = 0
        loss = 0
        honourable_mention = 0
        dishonourable_mention = 0
        self.set_up_contest_components(num_entrants=10)
        self.contest.close()
        self.score_contest()
        self.contest.judge()
        for entry in self.entries:
            entry.refresh_from_db()
            if entry.author.wins == 1:
                win += 1
            if entry.author.losses == 1:
                loss += 1
            if entry.author.hms == 1:
                honourable_mention += 1
            if entry.author.dms == 1:
                dishonourable_mention += 1
        self.assertTrue(win)
        self.assertTrue(honourable_mention)
        self.assertTrue(dishonourable_mention)
        # if not dishonourable_mention:
        # print("w: " + str(win) + " l:" + str(loss) + " dm:" + str(dishonourable_mention) + " hm:" + str(honourable_mention))
        self.assertTrue(loss)


class EntryModelTest(BaseAppTestCase):
    """Test A Entry"""

    def setUp(self):
        "Set up entry to test - requesires contest for context)" ""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.entry = Entry(
            contest=self.contest, story=self.stories[0], author=self.stories[0].author
        )
        self.entry.save()

    def test_entry_string_representation(self):
        """test str representation"""
        self.assertEqual(
            str(self.entry), str(self.entry.author) + " : " + self.entry.title
        )

    def test_entry_verbose_name_plural(self):
        """test verbose name plural"""
        self.assertEqual(str(Entry._meta.verbose_name_plural), "entries")


class CritModelTest(BaseAppTestCase):
    """Test A Crit"""

    def setUp(self):
        """set up"""
        self.set_up_contest(InternalJudgeContest)
        self.contest.save()
        self.set_up_contest_components()
        self.crit = Crit(entry=self.entries[0], reviewer=self.users[0])
        self.crit.save()

    def test_entry_string_representation(self):
        """test str"""
        self.assertEqual(
            str(self.crit),
            str(self.crit.entry.contest.title)
            + " : "
            + str(self.crit.reviewer.username)
            + " reviews "
            + str(self.crit.entry.author),
        )
        self.crit = Crit(entry=self.entries[0])
        self.assertEqual(
            str(self.crit), "ALERT - somehow this crit did not get set a title"
        )
