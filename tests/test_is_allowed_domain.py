from unittest import TestCase
from scraper import is_allowed_domain

class TestIsAllowedDomains(TestCase):
    def test_physics_domain(self):
        test_domain = "physics.uci.edu"

        assert is_allowed_domain(test_domain) == False

    def test_all_allowed_domains_and_subdomains(self):
        domains = [
            "ics.uci.edu",
            "cs.uci.edu",
            "informatics.uci.edu",
            "stat.uci.edu",
            "wics.ics.uci.edu",
            "ngs.cs.uci.edu",
            "stan.informatics.uci.edu",
            "wrong.stat.uci.edu"
        ]

        for domain in domains:
            assert is_allowed_domain(domain) == True
