from unittest import TestCase
from utils.deliverable_helpers import LongestPageHelper

class TestLongestPage(TestCase):
    """
    Tests to ensure LongestPageHelper updates its
    longest_page_and_count dictionary correctly
    """

    def test_smaller_pages_dont_update(self):
        LongestPageHelper.reset_longest_page()

        test1_url = "northside"
        test1_text = "they wishin they wishin they wishin on me"

        test2_url = "eastside"
        test2_text = "we used to hold hands man"

        test3_url = "southside"
        test3_text = "idk this song"

        LongestPageHelper.update_longest_page(test1_url, test1_text)
        LongestPageHelper.update_longest_page(test2_url, test2_text)
        LongestPageHelper.update_longest_page(test3_url, test3_text)

        output = LongestPageHelper.longest_page_and_count

        assert output["url"] == "northside"
        assert output["text_length"] == 8

    def test_larger_pages_update(self):
        LongestPageHelper.reset_longest_page()

        test1_url = "northside"
        test1_text = "they wishin they wishin they wishin on me"

        test2_url = "eastside"
        test2_text = "we used to hold hands man"

        test3_url = "southside"
        test3_text = "idk this song"

        LongestPageHelper.update_longest_page(test3_url, test3_text)
        LongestPageHelper.update_longest_page(test2_url, test2_text)
        LongestPageHelper.update_longest_page(test1_url, test1_text)

        output = LongestPageHelper.longest_page_and_count

        assert output["url"] == "northside"
        assert output["text_length"] == 8

    def test_same_length_page_dont_update(self):
        LongestPageHelper.reset_longest_page()

        test1_url = "runaway"
        test1_text = "love me till we reach the weekend"

        test2_url = "eastside"
        test2_text = "wonchu run away with me we're leaving"

        test3_url = "villain"
        test3_text = "knows what i am what i'm not"

        LongestPageHelper.update_longest_page(test1_url, test1_text)
        LongestPageHelper.update_longest_page(test2_url, test2_text)
        LongestPageHelper.update_longest_page(test3_url, test3_text)

        output = LongestPageHelper.longest_page_and_count

        assert output["url"] == "runaway"
        assert output["text_length"] == 7
