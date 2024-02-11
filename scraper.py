import re
from bs4 import BeautifulSoup, UnicodeDammit
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

from utils.deliverable_helpers import LongestPageHelper
from generate_unique_without_fragments import url_without_fragment
from cos_sim import compute_cosine_similarity
from utils.robots_helper import RobotsHelperFactory

# For cosine similarity, but cosine similarity takes a bit too long
# so these remain unused
unique_urls = set()
unique_contents = []


def scraper(url, resp, depth=0, max_depth=3,collected_texts=[]):
    
    #check dept avoid traps
    if depth > max_depth:
        return [], collected_texts
    
    links, text_content = extract_next_links(url, resp)
    #filter stopwords
    filtered_text = get_no_stop_words(text_content)
    #accumulate text content
    collected_texts.append(filtered_text)
    most_common_50 = get_50_most_common_words(collected_texts)

    # Print the 50 most common words with their frequencies
    print("The 50 most common words are:")
    for word, freq in most_common_50:
        print(f"{word}: {freq}")
    # print("check content ",collected_texts)
    
    valid_links = []
    with open("urls.txt", "w") as save_all_valid_urls:
        for link in links:
            if is_valid(link):
                save_all_valid_urls.write(link + "\n")
                valid_links.append(link)
    return valid_links,collected_texts

from collections import Counter
#take collected text from webpage and return 50 most common ones
def get_50_most_common_words(collected_texts):
    all_words = ' '.join(collected_texts).split()
    word_counts = Counter(all_words)
    most_common_50 = word_counts.most_common(50)
    return most_common_50

# load stop word from text file and return stop word
def load_stop_words(file_path):
    with open(file_path, 'r') as file:
        stop_words = set(file.read().strip().split('\n'))
    return stop_words


# This part is for detect no information 
def is_page_informative(page, max_words = 180):
    text_content = page.get_text().strip() # get text from page and remove ending space
    text_content = re.sub(r'[^a-zA-Z0-9]', ' ', text_content) # use regular expression to replace special characters with space
    tokens = re.findall(r'\w+', text_content, re.IGNORECASE) # get token
    if len(tokens) > max_words:
        return True
    return False

# This is for detect and avoid very large files
def is_large_file(soup, max_size_mb=5):
    content_length = soup.find("meta", attrs={"name": "content-length"}) # get the length of the html file
    if content_length:
        file_size = int(content_length["content"]) / (1024 * 1024) # transform to MB
        return file_size > max_size_mb
    return False

# return filtered text without stopwords
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


def has_repeating_dir(url: str):
    """Returns if a url has repeating directories, potentially indicating a trap"""
    parsed = urlparse(url)
    split_dirs = [i for i in parsed.path.split("/") if i != '']

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

    # Cosine Similarity code that takes a bit too long
    """
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
    """

    # Return a list with the hyperlinks (as strings) scraped from resp.raw_response.content
    hyperlinks = []

    if (resp.status != 200):
        return list(), ""
    
    rh, can_read_robots = RobotsHelperFactory.get_helper(url)

    soup = BeautifulSoup(resp.raw_response.content, "lxml")
    text = soup.get_text(separator=' ', strip=True)

    if not is_large_file(soup) and is_page_informative(soup):

        LongestPageHelper.update_longest_page(url, text)

        links = [link.get("href") for link in soup.findAll("a")]
        if can_read_robots:
            for link in rh.get_links_from_sitemap():
                links.append(link)

        for link_url in links:
            if link_url:
                link_url = link_url.strip()
                link_url = url_without_fragment(link_url)
            else:
                continue

            if is_valid(link_url) and not has_repeating_dir(link_url):

                if can_read_robots:
                    if rh.can_fetch(link_url):
                        hyperlinks.append(link_url)
                else:
                    hyperlinks.append(link_url)

    return hyperlinks,text

#add new url to history trap list
historytrap = set()
def add_history(url):
    historytrap.add(url)


def is_allowed_domain(netloc: str):
    """Restricts authority to only be in 4 domains"""
    if any(domain in netloc for domain in set([".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"])):
        return True
    
    if any(domain == netloc for domain in set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])):
        return True
    
    return False

# intake urls,  determine if urls are valid for scraping
def is_valid(url):
    if url in historytrap:
        # print("HERE ", url)
        return False
    key = True
    # Parse the URL into components.
    parsed = urlparse(url)

    if "ical" in parsed.query or "facebook" in parsed.query or "twitter" in parsed.query:
        key = False

    # Check if the URL's scheme is either HTTP or HTTPS. Invalidate otherwise.
    if parsed.scheme not in set(["http", "https"]):
        key = False

    if not is_allowed_domain(parsed.netloc):
        key = False

    try:
        #check urls with calender patterns
        if re.search(r'\/\d{4}[-\/]\d{2}[-\/]\d{2}\/|\/\d{4}[-\/]\d{2}\/', parsed.path.lower()):
            key=False
        
        file_filter = r"\.(css|js|bmp|gif|jpeg|jpg|ico|png|tiff|mid|mp2|mp3|mp4" \
                        r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                        r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat" \
                        r"|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                        r"|thmx|mso|arff|rtf|jar|csv|rm|smil|wmv|swf|wma|zip|rar|gz|bib" \
                        r"|a|asm|asp|awk|wk|bat|bmp|btm|BTM|c|class|cmd|CPP|csv|cur" \
                        r"|cxx|CXX|db|def|DES|dlg|dll|don|dpc|dpj|dtd|dump|dxp|eng|exe" \
                        r"|flt|fmt|font|fp|ft|gif|h|H|hdb |edabu|hdl |hid|hpp |hrc|src" \
                        r"|HRC|src|html|hxx|Hxx|HXX|ico|idl|IDL|ih|ilb|inc|inf|ini|inl" \
                        r"|ins|java|jar|jnl|jpg|js|jsp|kdelnk|l|lgt|lib|lin|ll|LN3|lng" \
                        r"|lnk|lnx|LOG|lst|olver|.lst|lst|olenv|m|mac|MacOS|map|mk|make" \
                        r"|MK|make|mod|NT2|o|obj|par|pfa|pfb|pl|PL|plc|pld|PLD|plf|pm" \
                        r"|pmk|pre|cpcomp|PRJ|prt|PS|ptr|r|rc|make|rdb |res|s|S|sbl" \
                        r"|scp|scr|sda|sdb|sdc|sdd|sdg|sdm|sds|sdv|sdw|sdi|seg|SEG" \
                        r"|Set|sgl|sh|sid|smf|sms|so|sob|soh|sob|soc|sod|soe|sog|soh" \
                        r"|src|srs|SSLeay|Static|tab|tex|TFM|thm|tpt|tsc|ttf|TTF|txt|TXT" \
                        r"|unx|UNX|urd|url|VMS|vor|W32|wav|wmf|xml|xpm|xrb|y|yxx|zip|)$"
        if re.search(file_filter, parsed.path.lower()) or re.search(file_filter, parsed.query):
            key = False
    except TypeError:
        print("TypeError for ", parsed)
        key = False

    # Invalidate URLs that are unusually long (over 200 characters).
    if len(url) > 200:
        key = False

    # Invalidate URLs with too many query parameters, potentially indicating a trap.
    # Checking logs shows that the only pages with at least 2 query parameters
    # are calendar or dynamic query traps
    if len(parse_qs(url)) >= 2:
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
    start_url = "https://www.ics.uci.edu/"

    # Start the scraping process
    _, collected_texts = scraper(start_url, download(start_url, config), 0, 3, [])

    # After scraping is done, analyze the collected texts to find the most common words
    most_common_50 = get_50_most_common_words(collected_texts)

    # Print the 50 most common words with their frequencies
    print("The 50 most common words are:")
    for word, freq in most_common_50:
        print(f"{word}: {freq}")
    # test_url = "http://sli.ics.uci.edu/Pubs/Pubs?action=download&upname=kdsd08.pdf"
    # test_url = "http://sli.ics.uci.edu/Classes/2015W-273a"
    # test_url = "https://wics.ics.uci.edu/annual-mentorship-program-2013/"
    test_url = "http://evoke.ics.uci.edu"
    test_url = "https://www.ics.uci.edu/faculty/profiles/view_faculty.php?ucinetid=klefstad"
    # test_url = "https://www.stat.uci.edu"
    test_url = "https://wics.ics.uci.edu/cropped-img_5885-2-2-jpg/"
    print("Split url:", urlparse(test_url))
    print()
    print("Is valid URL:", is_valid(test_url))
    print()
    print("is repeating:", has_repeating_dir(test_url))
    print()

    resp = download(test_url, config)

    print("status:", resp.status)
    print()

    soup = BeautifulSoup(resp.raw_response.content, "lxml")
    text = soup.get_text(separator=' ', strip=True)
    
    # links = extract_next_links(test_url, resp)
    # print(links)
    print()

    print("status is not 200?", resp.status != 200)
    print()
    print("text of page:", text)