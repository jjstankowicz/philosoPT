from philo.questioner import Questioner


class TestQuestioner(unittest.TestCase):
    def setUp(self):
        self.questioner = Questioner()
        return super().__init__()
    
    def test_write_history(self):
        self.questioner.write_history()
        # Check that the history has been written to a file
        with open("history.json", "r") as f:
            history = f.read()
        self.assertIsInstance(history, str, "History is not a string")
        self.assertGreater(len(history), 0, "History is empty")