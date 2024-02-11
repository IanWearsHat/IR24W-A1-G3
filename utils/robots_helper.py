from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import requests
import socket


class RobotsHelper:
    def __init__(self, base_url: str):
        parsed = urlparse(base_url)
        base_url = parsed.netloc

        if '/' == base_url[-1]:
            base_url = base_url[:-1]

        timeout_seconds = 1
        socket.setdefaulttimeout(timeout_seconds)

        self.robots_path = base_url + "/robots.txt"
        self.rp = RobotFileParser()
    
    def robots_file_exists(self) -> bool:
        resp = requests.get(self.robots_path)
        return resp.status_code == 200

    def has_read_robots_url(self) -> bool:
        try:
            self.rp.set_url(self.robots_path)
            self.rp.read()
        except:
            return False

        return True
    
    def can_fetch(self, url: str) -> bool:
        return self.rp.can_fetch("*", url)


if __name__ == "__main__":
    rh = RobotsHelper("https://www.informatics.uci.edu")
    if rh.robots_file_exists and rh.has_read_robots_url():
        print(rh.can_fetch("https://www.informatics.uci.edu/support/champion-research"))
    else:
        print("doesnt exist")
