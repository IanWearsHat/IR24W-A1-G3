class LongestPageHelper:
    longest_page_and_count = {
        "url": "",
        "text_length": -1,
    }

    @classmethod
    def update_longest_page(cls, url: str, text: str) -> None:
        """Updates the longest page dict if the input text word count is longer"""

        text_length = LongestPageHelper.longest_page_and_count["text_length"]
        word_count = len(text.split())
        if word_count > text_length:
            LongestPageHelper.longest_page_and_count["url"] = url
            LongestPageHelper.longest_page_and_count["text_length"] = word_count
    
    @classmethod
    def reset_longest_page(cls) -> None:
        """Resets the longest page dict (mainly for testing)"""
        LongestPageHelper.longest_page_and_count = {
            "url": "",
            "text_length": -1,
        }


class SubdomainCountHelper:
    @classmethod
    def get_subdomain_count(urls_file_name: str) -> int:
        """Returns the number of subdomains in the ics.uci.edu domain"""
        pass

    @classmethod
    def create_sorted_subdomain_file(urls_file_name: str) -> None:
        """
        Creates a list of subdomains ordered alphabetically with
        their number of unique pages in each line

        - ex. A line in this list would be: http://vision.ics.uci.edu, 10

        """
        pass
