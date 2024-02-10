from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

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
    def create_longest_page_file(cls) -> None:
        """Creates a file detailing the longest page and its word count"""
        with open("deliverable_question_2.txt", "w", encoding="utf-8") as w_file:
            url = LongestPageHelper.longest_page_and_count["url"]
            text_length = LongestPageHelper.longest_page_and_count["text_length"]
            to_write = f"Longest Page URL: {url}\nLongest Page Length: {text_length}"

            w_file.write(to_write)

    @classmethod
    def reset_longest_page(cls) -> None:
        """Resets the longest page dict (mainly for testing)"""
        LongestPageHelper.longest_page_and_count = {
            "url": "",
            "text_length": -1,
        }


class SubdomainCountHelper:
    @classmethod
    def _create_subdomain_to_page_dict(cls, urls_file_name: str) -> dict[str, set]:
        """Returns a dict where the key-value pair is url to set of paths for that url"""
        subdomain_to_page = {}
        with open(urls_file_name, "r", encoding="utf-8") as url_file:
            for url in url_file:
                parsed = urlparse(url)
                netloc = parsed.netloc

                if ".ics.uci.edu" not in netloc:
                    continue

                if netloc not in subdomain_to_page:
                    subdomain_to_page[netloc] = set()
                else:
                    subdomain_to_page[netloc].add(parsed.path)

        return subdomain_to_page
    
    @classmethod
    def create_sorted_subdomain_file(cls, urls_file_name: str) -> None:
        """
        Creates a list of ics.uci.edu subdomains ordered alphabetically with
        their number of unique pages in each line

        Also counts the number of unique subdomains on the last line

        - ex. A line in this list would be: http://vision.ics.uci.edu, 10
        """
        subdomain_to_page = SubdomainCountHelper._create_subdomain_to_page_dict(urls_file_name)
        subdomain_to_page = dict(sorted(subdomain_to_page.items()))

        with open("deliverable_question_4.txt", "w", encoding="utf-8") as w_file:
            for domain in subdomain_to_page:
                page_count= len(subdomain_to_page[domain])
                to_write = f"{domain}, {page_count}\n"

                w_file.write(to_write)

            subdomain_count = len(subdomain_to_page.keys())
            to_write = f"Number of subdomains: {subdomain_count}"
            w_file.write(to_write)


if __name__ == "__main__":
    # SubdomainCountHelper.create_sorted_subdomain_file("urls.txt")

    rp = RobotFileParser()
    rp.set_url("https://en.wikipedia.org/robots.txt")
    rp.read()
    print(rp.can_fetch("*", "https://en.wikipedia.org/wiki/Main_Page"))
