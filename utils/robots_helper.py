from urllib.robotparser import RobotFileParser
import requests
import socket


class RobotsHelper:
    def __init__(self, base_url: str):
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
    rh = RobotsHelper("https://docs.python.org/")
    if rh.robots_file_exists and rh.has_read_robots_url():
        print(rh.can_fetch("https://docs.python.org/a"))
    else:
        print("doesnt exist")
