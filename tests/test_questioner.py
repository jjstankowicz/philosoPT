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
        self.actions = [
            "Donating to a cause you do not believe in.",
            "Donating to any charitable cause.",
            "Killing five people instead of one in the trolley car problem",
        ]
        self.multiple_philosophies_and_descriptions = [
            {
                "name": "Anarchism",
                "description": "A political philosophy that advocates self-governed societies with voluntary institutions.",
            },
            self.philosophy_and_description,
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
            force_refresh=False,
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
        clusters_to_actions = self.questioner.get_clusters_to_actions(
            prompt_version_number=0,
            action_list=self.actions,
            pbar=True,
            force_refresh=False,
        )
        # Verify that the cluster_labels is a list of strings
        self.assertIsInstance(self.questioner.cluster_labels, list, "cluster_labels is not a list")
        self.assertIsInstance(
            self.questioner.cluster_labels[0], str, "cluster_labels[0] is not a string"
        )
        # Verify the action_clusters is a list of dictionaries
        action_clusters = self.questioner.collect_action_clusters
        self.assertIsInstance(action_clusters, list, "action_clusters is not a list")
        self.assertIsInstance(action_clusters[0], dict, "action_clusters[0] is not a dictionary")
        # Verify that the keys of the first dictionary in action_clusters "action", "cluster", "aligned"
        for key in ["action", "cluster", "aligned"]:
            self.assertIn(key, action_clusters[0].keys(), f"{key} key not found")
        # Verify that the cluster_to_actions is a dictionary
        internal_cluster_to_actions = self.questioner.cluster_to_actions_dict
        self.assertIsInstance(
            internal_cluster_to_actions, dict, "cluster_to_actions is not a dictionary"
        )
        first_key = list(internal_cluster_to_actions.keys())[0]
        # Verify that the first key in cluster_to_actions is a list of dictionaries
        self.assertIsInstance(
            internal_cluster_to_actions[first_key],
            list,
            "cluster_to_actions[first_key] is not a list",
        )
        self.assertIsInstance(
            internal_cluster_to_actions[first_key][0],
            dict,
            "cluster_to_actions[first_key][0] is not a dictionary",
        )
        # Confirm that clusters_to_actions == cluster_to_actions
        self.assertEqual(
            clusters_to_actions,
            internal_cluster_to_actions,
            "clusters_to_actions != internal_cluster_to_actions",
        )

    def test_get_action_scores(self):
        action_scores = self.questioner.get_action_scores(
            prompt_version_number=0,
            action_list=self.actions,
            philosophy_list=self.multiple_philosophies_and_descriptions,
            verbose=False,
            pbar=False,
            force_refresh=False,
        )
        # Verify that the action_scores is a list of dictionaries
        self.assertIsInstance(action_scores, list, "action_scores is not a list")
        self.assertIsInstance(action_scores[0], dict, "action_scores[0] is not a dictionary")
        # Verify that the keys of the dictionary in action_scores are "action", "philosophy", "morality", "reason"
        for key in ["action", "philosophy", "morality", "reason"]:
            self.assertIn(key, action_scores[0].keys(), f"{key} key not found")
        # Verify that the length of the output is equal the the length of action list times the length of philosophy list
        len_action_scores = len(action_scores)
        len_action_list = len(self.actions)
        len_philosophy_list = len(self.multiple_philosophies_and_descriptions)
        self.assertEqual(
            len_action_scores,
            len_action_list * len_philosophy_list,
            "Length of action_scores is not equal to length of action list times length of philosophy list",
        )
