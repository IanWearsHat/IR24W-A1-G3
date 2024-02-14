import os
import shelve

from threading import Thread, RLock
from queue import Queue, Empty
from urllib.parse import urlparse

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.queue_pointer = 0
        self.to_be_downloaded = {
            "ics.uci.edu": Queue(),
            "cs.uci.edu": Queue(),
            "informatics.uci.edu": Queue(),
            "stat.uci.edu": Queue(),
        }
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                domain = self.get_domain(urlparse(url))
                self.to_be_downloaded[domain].put(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")
        
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

    def all_queues_empty(self):
        for domain in self.to_be_downloaded.keys():
            if not self.to_be_downloaded[domain].empty():
                return False
        return True

    def get_tbd_url(self):
        try:
            while True:
                domain = self.to_be_downloaded.keys()[self.queue_pointer]
                queue = self.to_be_downloaded[domain]
                if queue.empty():
                    if self.all_queues_empty():
                        raise Empty
                    continue
                else:
                    return queue.get(block=True, timeout=3)
        except IndexError:
            return None

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            self.save[urlhash] = (url, False)
            self.save.sync()
            domain = self.get_domain(urlparse(url))
            self.to_be_downloaded[domain].put(url)
    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self.save[urlhash] = (url, True)
        self.save.sync()
