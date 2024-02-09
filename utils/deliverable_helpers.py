class LongestPageHelper:
    longest_page_and_count = {
        "url": "",
        "text_length": -1,
    }

    @classmethod
    def update_longest_page(cls, url: str, text: str) -> None:
        text_length = LongestPageHelper.longest_page_and_count["text_length"]
        word_count = len(text.split())
        if word_count > text_length:
            LongestPageHelper.longest_page_and_count["url"] = url
            LongestPageHelper.longest_page_and_count["text_length"] = word_count
    
    @classmethod
    def reset_longest_page(cls) -> None:
        LongestPageHelper.longest_page_and_count = {
            "url": "",
            "text_length": -1,
        }
