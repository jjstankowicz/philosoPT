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
        self.action_clusters = [
            "Donating to a cause you do not believe in.",
            "Donating to any charitable cause.",
            "Killing five people instead of one in the trolley car problem",
        ]
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
        # Verify that the actions_from_philosopy is a list of dictionaries
        self.assertIsInstance(
            actions_from_philosopy,
            list,
            "actions_from_philosopy is not a list",
        )
        self.assertIsInstance(
            actions_from_philosopy[0],
            dict,
            "actions_from_philosopy[0] is not a dictionary",
        )

    def test_get_action_clusters(self):
        self.questioner.get_action_clusters(
            prompt_version_number=0,
            action_list=self.action_clusters,
        )
        # Verify that the cluster_labels is a list of strings
        self.assertIsInstance(
            self.questioner.cluster_labels,
            list,
            "cluster_labels is not a list",
        )
        self.assertIsInstance(
            self.questioner.cluster_labels[0],
            str,
            "cluster_labels[0] is not a string",
        )
