import re
from lxml import html
from bs4 import UnicodeDammit, BeautifulSoup
from urllib.parse import urlparse


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
    # Return a list with the hyperlinks (as strings) scraped from resp.raw_response.content

    debug = True

    hyperlinks = []

    if (resp.status != 200):
        return list()

    soup = BeautifulSoup(resp.raw_response.content, "lxml")
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
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
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
