from unittest import TestCase
from scraper import has_repeating_dir

class TestRepeatingSubdirs(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestRepeatingSubdirs, self).__init__(*args, **kwargs)
        self.base_url = "https://www.bruh.com/"

    def test_simple_repeat(self):
        test_url = self.base_url
        for _ in range(2):
            test_url += "nani/"

        assert has_repeating_dir(test_url) == True

    def test_two_repeats(self):
        test_url = self.base_url
        subdirs = ["nani", "bruh"]
        for _ in range(2):
            for subdir in subdirs:
                test_url += subdir + '/'

        assert has_repeating_dir(test_url) == True

    def test_five_repeats(self):
        test_url = self.base_url
        subdirs = ["nani", "bruh", "why", "wing", "hacken"]
        for _ in range(2):
            for subdir in subdirs:
                test_url += subdir + '/'

        assert has_repeating_dir(test_url) == True
    
    def test_has_no_repeats(self):
        test_url = self.base_url
        test_url += "bruh/"

        assert has_repeating_dir(test_url) == False
