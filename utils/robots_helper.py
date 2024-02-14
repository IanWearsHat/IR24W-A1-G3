from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import requests
import socket

class RobotsHelper:
    """
    Helper for reading robots and sitemaps.
    Essentially a wrapper for urllib.robotparser.RobotFileParser
    """
    sitemaps_seen = set()

    def __init__(self, base_url: str):
        """Sets a robots.txt path and creates a RobotFileParser"""
        parsed = urlparse(base_url)
        base_url = parsed.scheme + "://" + parsed.netloc

        if '/' == base_url[-1]:
            base_url = base_url[:-1]

        # timeout_seconds = 1
        # socket.setdefaulttimeout(timeout_seconds)

        self.robots_path = base_url + "/robots.txt"

        self.rp = RobotFileParser()

    def read_robots_url(self) -> bool:
        """
        Reads the robots.txt path
        
        Doing this on initialization seems to run into a read timeout error.
        """
        try:
            self.rp.set_url(self.robots_path)
            self.rp.read()
        except Exception as e:
            print(e)
            return False

        return True

    def can_fetch(self, url: str) -> bool:
        return self.rp.can_fetch("*", url)
    
    def _get_sitemap_links(self, sitemap_url: str) -> list:
        """
        Returns the sitemap links given a url.

        If there are sitemaps within the sitemap, the function
        recursively runs until we reach the actual child urls.
        """
        links = []
    
        r = requests.get(sitemap_url)
        soup = BeautifulSoup(r.content, features="xml")
        sitemap_tags = soup.find_all("sitemap")
        if sitemap_tags:
            for sitemap in sitemap_tags:
                for link in self._get_sitemap_links(sitemap.findNext("loc").text):
                    links.append(link)
        else:
            loc = soup.find_all("loc")
            for link in loc:
                links.append(link.text)

        return links
    
    def get_links_from_sitemap(self) -> list:
        """
        Public function that also checks if the sitemap has been seen
        to not recursively call.
        """
        if self.robots_path in RobotsHelper.sitemaps_seen:
            return list()

        links = []
        sitemaps = self.rp.site_maps()

        if sitemaps:
            for sitemap in sitemaps:
                for link in self._get_sitemap_links(sitemap):
                    links.append(link)
        
        RobotsHelper.sitemaps_seen.add(self.robots_path)
        return links


class RobotsHelperFactory:
    """
    Only has one function to get a RobotsHelper

    The purpose of this class is to keep track of if a
    RobotsHelper was already created for a domain to
    improve runtime.
    """
    robot_helpers = {}

    @classmethod
    def get_helper(cls, url: str) -> tuple[RobotsHelper, bool]:
        """
        If a RobotHelper was already created in the robot_helpers dict,
        return that and whether or not robots was read successfully.

        Otherwise, create a new RobotHelper object and attempt to read robots.txt.
        """
        parsed = urlparse(url)
        if parsed.netloc in RobotsHelperFactory.robot_helpers:
            rh, has_read = RobotsHelperFactory.robot_helpers[parsed.netloc]
            return rh, has_read
        
        rh = RobotsHelper(url)
        has_read = rh.read_robots_url()
        RobotsHelperFactory.robot_helpers[parsed.netloc] = (rh, has_read)

        return rh, has_read


if __name__ == "__main__":
    # rh = RobotsHelper("https://www.informatics.uci.edu")
    # if rh.robots_file_exists():
    #     print(rh.can_fetch("https://www.informatics.uci.edu/support/champion-research") == True)
    # else:
    #     print("doesnt exist")
    # rh = RobotsHelper("https://wics.ics.uci.edu")
    # rh.read_robots_url()
    # import datetime
    # p = datetime.datetime.now()
    # print(rh.get_links_from_sitemap())
    # print(datetime.datetime.now() - p)
    # print(rh.get_links_from_sitemap())

    url = "https://www.ics.uci.edu"
    url2 = "https://ics.uci.edu"

    print(urlparse(url))
    print(urlparse(url2))