import logging
import re
from bs4 import BeautifulSoup, UnicodeDammit
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
import urllib.robotparser
from urllib.error import URLError
import hashlib

def scraper(url, resp, depth=0, max_depth=3):
    # if not is_crawl_allowed(url):
    #     print(f"Crawling disallowed by robots.txt: {url}")
    #     return []
    if depth > max_depth:
        return []

    links = extract_next_links(url, resp)
    valid_links = []
    with open("urls.txt", "a") as save_all_valid_urls:
        for link in links:
            if is_valid(link):
                save_all_valid_urls.write(link + "\n")
                valid_links.append(link)
    return valid_links

def normalize_url(url):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    filtered_query = {k: v for k, v in query.items() if k not in ['sessionid', 'tracking']}
    normalized_url = parsed_url._replace(query=urlencode(filtered_query, doseq=True))
    return urlunparse(normalized_url)

# def is_crawl_allowed(target_url, user_agent='*'):
#     rp = urllib.robotparser.RobotFileParser()
#     parsed_url = urlparse(target_url)
#     robots_txt_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
#     rp.set_url(robots_txt_url)
#     try:
#         rp.read()
#     except URLError as e:
#         print(f"Error accessing robots.txt for {target_url}: {e.reason}. Proceeding with caution.")
#         return True  # Default to allowing crawling on URLError to proceed with caution.
#     except Exception as e:
#         print(f"Unexpected error when checking robots.txt for {target_url}: {e}")
#         return False  # Default to not allowing crawling on unexpected errors.
    return rp.can_fetch(user_agent, target_url)

def load_stop_words(file_path):
    with open(file_path, 'r') as file:
        return set(file.read().strip().split('\n'))

def decode_html(html_string):
    converted = UnicodeDammit(html_string)
    if not converted.unicode_markup:
        raise UnicodeDecodeError("Failed to detect encoding, tried [%s]" % ', '.join(converted.tried_encodings))
    return converted.unicode_markup

historytrap = set()
def add_history(url):
    
     historytrap.add(url)
    
def is_page_informative(page, max_words = 100):
    text_content = page.get_text().strip() # get text from page and remove ending space
    text_content = re.sub(r'[^a-zA-Z0-9]', ' ', text_content) # use regular expression to replace special characters with space
    tokens = re.findall(r'\w+', text_content, re.IGNORECASE) # get token
    if len(tokens) > max_words:
        return True
    return False

def is_large_file(soup, max_size_mb=5):
    content_length = soup.find("meta", attrs={"name": "content-length"}) # get the length of the html file
    if content_length:
        file_size = int(content_length["content"]) / (1024 * 1024) # transform to MB
        return file_size > max_size_mb
    return False

def extract_next_links(url, resp):
    hyperlinks = []
    if resp.status == 200:
        soup = BeautifulSoup(resp.raw_response.content, "lxml")
        if not is_large_file(soup) and is_page_informative(soup):
            a_tags = soup.findAll("a")
            for link in a_tags:
                content = link.get("href")
                if content:
                    content = content.strip()
                else:
                    continue
                if "https" in content or "http" in content:
                    hyperlinks.append(content)
    return hyperlinks

import re
from urllib.parse import urlparse



def is_valid(url):
    
        if url in historytrap:
            print("HERE ",url)
            return False
        key = True
        # Parse the URL into components.
        parsed = urlparse(url)
        
        # Parse the query parameters from the URL
        params = parse_qs(parsed.query)
        # Construct base URL without query parameters.
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # # Check for increasing sequence in the parameters which might indicate a trap.
        # for param, values in params.items():
        #     for value in values:
        #         if self.is_increasing_sequence(base_url, param, value):
        #             # Detected a potential trap based on parameter sequence.
        #             return False

        # Check if the URL's scheme is either HTTP or HTTPS. Invalidate otherwise.
        if parsed.scheme not in set(["http", "https"]):
            key = False
        try:
            # Check if the hostname contains '.ics.uci.edu'.
            if ".ics.uci.edu" not in parsed.hostname:
                key = False
            if re.search(r'\/\d{4}\/\d{2}\/\d{2}\/|\/\d{4}\/\d{2}\/', parsed.path.lower()):
                key=False
           
            if re.search(r"\.(css|js|bmp|gif|jpeg|jpg|ico|png|tiff|mid|mp2|mp3|mp4"
                         r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                         r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1"
                         r"|thmx|mso|arff|rtf|jar|csv"
                         r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
                valid = False
        except TypeError:
            print("TypeError for ", parsed)
            key = False

        # Invalidate URLs that are unusually long (over 200 characters).
        if len(url) > 200:
            key = False

        # # Invalidate URLs where a single path segment is repeated (a common trap pattern).
        # path_segments = parsed.path.split('/')
        # if any(path_segments.count(segment) > 1 for segment in path_segments):
        #     valid = False

        # Invalidate URLs with too many query parameters, potentially indicating a trap.
        if len(parsed.query.split('&')) > 10:
            key = False


        # If the URL is found to be invalid, update the trap counter.
        if not key:
           add_history(url)

        return key
