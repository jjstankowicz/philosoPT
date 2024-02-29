import unittest
import os
from philo.questioner import Questioner


class TestQuestioner(unittest.TestCase):

    def setUp(self):
        self.questioner = Questioner(history_filename_suffix="_test")
        self.philosophy_and_description = {
            "name": "Utilitarianism",
            "description": "A philosophy that emphasizes the greatest good for the greatest number, often associated with Jeremy Bentham and John Stuart Mill.",
        }
        return super().__init__()

    def test_get_philosophies(self):
        self.questioner.get_philosophies(prompt_version_number=0)
        # Get the timestamp of the self.questioner.history_file_path file
        timestamp = os.path.getmtime(self.questioner.history_file_path)
        # Create a new questioner with a fresh start
        new_questioner = Questioner(fresh_start=True, history_filename_suffix="_test")
        # Get the timestamp of the new_questioner.history_file_path file
        new_timestamp = os.path.getmtime(new_questioner.history_file_path)
        # Verify that the new timestamp is greater than the old timestamp
        self.assertGreater(
            new_timestamp,
            timestamp,
            "New timestamp is not greater than old timestamp",
        )

    def test_get_actions_from_philosophies(self):
        actions_from_philosopy = self.questioner.get_actions_from_philosophies(
            prompt_version_number=0,
            philosophy_dict=self.philosophy_and_description,
        )
        import pdb

        pdb.set_trace()
