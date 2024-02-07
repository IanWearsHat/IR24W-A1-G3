import re
from lxml import html
from bs4 import UnicodeDammit, BeautifulSoup
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def scraper(url, resp):
    links = extract_next_links(url, resp)
    valid_links = []
    save_all_valid_urls = open("urls.txt", "a")
    for link in links:
        if is_valid(link):
            save_all_valid_urls.write(link + "\n")
            valid_links.append(link)
    save_all_valid_urls.close()
    return valid_links


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
    """
    Uses Beautiful Soup to detect encoding.
    
    Returns Unicode string if successful

    Code taken from lxml docs at the website below:
    https://lxml.de/elementsoup.html#:~:text=(tag_soup)-,Using%20only%20the%20encoding%20detection,-Even%20if%20you
    """
    converted = UnicodeDammit(html_string)
    if not converted.unicode_markup:
        raise UnicodeDecodeError(
            "Failed to detect encoding, tried [%s]",
            ', '.join(converted.tried_encodings))

    return converted.unicode_markup


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
                if "https" in content or "http" in content:
                    hyperlinks.append(content)
    return hyperlinks

    # Return a list with the hyperlinks (as strings) scraped from resp.raw_response.content

    debug = True

    hyperlinks = []

    if (resp.status != 200):
        return list()

    soup = BeautifulSoup(resp.raw_response.content, "lxml")

    # text = soup.get_text(separator=' ', strip=True)
    # get_no_stop_words(text)

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



def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    url_paths = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"]
    try:
        path_match = False
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if parsed.hostname is None:
            return False
        for path in url_paths:
            if path in parsed.hostname:
                path_match = True
        
        return path_match and not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
