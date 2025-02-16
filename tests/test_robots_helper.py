from unittest import TestCase
from utils.robots_helper import RobotsHelper

class TestRobotsHelper(TestCase):
    """
    Tests that the robots file is read can determine if
    fetching a url is polite or not
    """
    def test_robots_file_can_fetch_returns_correctly(self):
        rh = RobotsHelper("https://www.informatics.uci.edu")
        rh.read_robots_url()

        assert rh.can_fetch("https://www.informatics.uci.edu/support/champion-research") == True
        assert rh.can_fetch("https://www.informatics.uci.edu/research/") == False
