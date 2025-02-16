from threading import Thread, Event, Lock
from queue import Empty
from urllib.parse import urlparse

from inspect import getsource
from utils.download import download
from utils import get_logger
from utils.deliverable_helpers import LongestPageHelper
import scraper
import time


class Worker(Thread):
    # reading from a dict is inherently thread-safe, no need for explicit lock
    # https://docs.python.org/3/glossary.html#term-global-interpreter-lock
    events = {
        "ics.uci.edu": (Event(), Lock()),
        "cs.uci.edu": (Event(), Lock()),
        "informatics.uci.edu": (Event(), Lock()),
        "stat.uci.edu": (Event(), Lock()),
    }

    all_workers = {}

    def __init__(self, worker_id, config, frontier):
        for _, event in Worker.events.items():
            event[0].set()

        Worker.all_workers[worker_id] = Event()

        self.worker_id = worker_id
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)

    @classmethod
    def all_threads_stopped(cls):
        for worker in Worker.all_workers.keys():
            if not Worker.all_workers[worker].is_set():
                return False
        return True

    def get_domain(self, netloc):
        before_set = set([".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"])
        after_set = set(["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"])

        for domain in before_set:
            if domain in netloc:
                return domain[1:]
        
        for domain in after_set:
            if domain in netloc:
                return domain

        return None

    def run(self):
        
        collected_texts = []
        while True:
            Worker.all_workers[self.worker_id].clear()
            try:
                tbd_url = self.frontier.get_tbd_url()
            except Empty:
            # if not tbd_url:
                Worker.all_workers[self.worker_id].set()
                time.sleep(1)
                if not Worker.all_threads_stopped():
                    continue

                self.logger.info("Frontier is empty. Stopping Crawler.")
                LongestPageHelper.create_longest_page_file(self.worker_id)
                most_common_50 = scraper.get_50_most_common_words(collected_texts)
                with open(f"{self.worker_id}_deliverable_question_3.txt", "w") as w_file:
                    for word, freq in most_common_50:
                        w_file.write(f"{word}: {freq}\n")
                break
            
            thread_debugging_enabled = False

            domain = urlparse(tbd_url).netloc
            domain = self.get_domain(domain)
            event_used, event_lock = Worker.events[domain]
            with event_lock:
                just_waited = False
                if not event_used.is_set():
                    if thread_debugging_enabled:
                        self.logger.info(f"Waiting for {domain}")
                    event_used.wait()
                    just_waited = True
                if thread_debugging_enabled:
                    self.logger.info(f"Using {domain}")
                event_used.clear()
                if just_waited:
                    time.sleep(self.config.time_delay / 2)
                time.sleep(self.config.time_delay / 2)

            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls, collected_texts = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

            
            event_used.set()
            if thread_debugging_enabled:
                self.logger.info(f"{domain} freed")
            time.sleep(self.config.time_delay)
