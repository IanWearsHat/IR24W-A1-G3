import logging
import re
from bs4 import BeautifulSoup, UnicodeDammit
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse
import urllib.robotparser
from urllib.error import URLError
import hashlib
from lxml import html
from bs4 import UnicodeDammit, BeautifulSoup
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from generate_unique_without_fragments import url_without_fragment
from cos_sim import compute_cosine_similarity

unique_urls = set()
unique_contents = []

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


def load_stop_words(file_path):
    with open(file_path, 'r') as file:
        stop_words = set(file.read().strip().split('\n'))
    return stop_words


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


def get_no_stop_words(page_text: str):
    stop_words_file = "stopword.txt"
    stop_words = load_stop_words(stop_words_file)
    words = page_text.split()
    filtered_text = ' '.join([word for word in words if word.lower() not in stop_words])
    return filtered_text


def decode_html(html_string):
    converted = UnicodeDammit(html_string)
    if not converted.unicode_markup:
        raise UnicodeDecodeError("Failed to detect encoding, tried [%s]" % ', '.join(converted.tried_encodings))
    return converted.unicode_markup


# TODO: see if "no data" means like one word or something
# ex. "http://sli.ics.uci.edu/Pubs/Pubs?action=download&upname=kdsd08.pdf"
# gives "Forbidden" which isn't really anything
def has_no_page_data(soup_text: str) -> bool:
    """
    Detect if there is any text content on the webpage.

    Handles "dead URLs that return a 200 status but no data"
    """
    return len(soup_text) == 0


def has_repeating_dir(url: str):
    parsed = urlparse(url)
    split_dirs = parsed.path.split("/")

    return len(set(split_dirs)) != len(split_dirs)


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!

    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    # <a href="https://xxxx"></a>
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
                if content in unique_urls:
                    continue
                if "https" in content or "http" in content:
                    url = url_without_fragment(content)
                    # url_contents = soup.get_text().strip()
                    # is_similar = False
                    # for content in url_contents:
                    #     sim = compute_cosine_similarity(content, url_contents)
                    #     if sim > 0.9:
                    #         is_similar = True
                    #         break
                    # if is_similar:
                    #     continue
                    unique_urls.add(url)
                    hyperlinks.append(url)
                    # unique_contents.append(url_contents)
    return hyperlinks

    # Return a list with the hyperlinks (as strings) scraped from resp.raw_response.content

    debug = True

    hyperlinks = []

    if (resp.status != 200):
        return list()

    soup = BeautifulSoup(resp.raw_response.content, "lxml")

    text = soup.get_text(separator=' ', strip=True)

    # TODO: maybe have all trap checks in one function
    if has_no_page_data(text):
        return list()

    if not is_large_file(soup) and is_page_informative(soup):
        a_tags = soup.findAll("a")
        for link in a_tags:
            content = link.get("href")
            if content:
                content = content.strip()
            else:
                continue
            # TODO: in the below if check, use is_valid
            if is_valid(url) and not has_repeating_dir(url):
                hyperlinks.append(content)
    
    return hyperlinks


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


def is_allowed_domain(netloc: str):
    if any(domain in netloc for domain in set([".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"])):
        return True
    
    if any(domain == netloc for domain in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])):
        return True
    
    return False


def is_valid(url):
    if url in historytrap:
        print("HERE ", url)
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

    if not is_allowed_domain(parsed.netloc):
        key = False

    try:
        if re.search(r'\/\d{4}\/\d{2}\/\d{2}\/|\/\d{4}\/\d{2}\/', parsed.path.lower()):
            key=False
        
        if re.search(r"\.(css|js|bmp|gif|jpeg|jpg|ico|png|tiff|mid|mp2|mp3|mp4"
                        r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                        r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat"
                        r"|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1"
                        r"|thmx|mso|arff|rtf|jar|csv|rm|smil|wmv|swf|wma|zip|rar|gz"
                        r"|a|asm|asp|awk|wk|bat|bmp|btm|BTM|c|class|cmd|CPP|csv|cur"
                        r"|cxx|CXX|db|def|DES|dlg|dll|don|dpc|dpj|dtd|dump|dxp|eng|exe"
                        r"|flt|fmt|font|fp|ft|gif|h|H|hdb |edabu|hdl |hid|hpp |hrc|src"
                        r"|HRC|src|html|hxx|Hxx|HXX|ico|idl |IDL|ih|ilb|inc|inf|ini|inl"
                        r"|ins|java|jar|jnl|jpg|js|jsp|kdelnk|l|lgt|lib|lin|ll|LN3|lng"
                        r"|lnk|lnx|LOG|lst|olver|.lst|lst|olenv|mac|MacOS|map|mk|make"
                        r"|MK|make|mod|NT2|o|obj|par|pfa|pfb|pl|PL|plc|pld|PLD|plf|pm"
                        r"|pmk|pre|cpcomp|PRJ|prt|PS|ptr|r|rc|make|rdb |res|s|S|sbl"
                        r"|scp|scr|sda|sdb|sdc|sdd|sdg|sdm|sds|sdv|sdw|sdi|seg|SEG"
                        r"|Set|sgl|sh|sid|smf|sms|so|sob|soh|sob|soc|sod|soe|sog|soh"
                        r"|src|srs|SSLeay|Static|tab|TFM|thm|tpt|tsc|ttf|TTF|txt|TXT"
                        r"|unx|UNX|urd|url|VMS|vor|W32|wav|wmf|xml|xpm|xrb|y|yxx|zip|)$", parsed.path.lower()):
            key = False
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


if __name__ == '__main__':
    from utils.download import download
    from utils.config import Config
    from utils.server_registration import get_cache_server
    from configparser import ConfigParser

    cparser = ConfigParser()
    cparser.read("config.ini")
    config = Config(cparser)
    config.cache_server = get_cache_server(config, False)

    # test_url = "http://sli.ics.uci.edu/Pubs/Pubs?action=download&upname=kdsd08.pdf"
    # test_url = "http://sli.ics.uci.edu/Classes/2015W-273a"
    # test_url = "https://wics.ics.uci.edu/annual-mentorship-program-2013/"
    test_url = "http://evoke.ics.uci.edu"
    test_url = "https://www.ics.uci.edu/faculty/profiles/view_faculty.php?ucinetid=klefstad"
    print("Split url:", urlparse(test_url))
    print()
    print("Is valid URL:", is_valid(test_url))
    print()

    resp = download(test_url, config)

    print("status:", resp.status)
    print()

    soup = BeautifulSoup(resp.raw_response.content, "lxml")
    text = soup.get_text(separator=' ', strip=True)
    
    links = extract_next_links(test_url, resp)
    print(links)
    print()

    print("status is not 200?", resp.status != 200)
    print()
    print("text of page:", text)