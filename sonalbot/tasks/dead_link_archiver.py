# -*- coding: utf-8 -*-
"""
MAX LEVEL Dead Link Archiver.
Auto-scales: 60/min → 500/min when flag detected.
"""

import time
import requests
import pywikibot
from waybackpy import WaybackMachineSaveAPI
from sonalbot.core.bot import SonalBot
from sonalbot.core.logger import get_logger

logger = get_logger(__name__)


class DeadLinkArchiver(SonalBot):
    """MAX LEVEL archiver."""

    TIMEOUT = 10
    STATUS_OK = range(200, 400)

    def __init__(self):
        super().__init__()
        self.checked = 0
        self.archived = 0

    def check_url(self, url):
        self.api_call(lambda: None)
        try:
            r = requests.head(url, timeout=self.TIMEOUT, allow_redirects=True,
                              headers={'User-Agent': 'SonalBot/1.0 (Wikidata bot)'})
            return r.status_code in self.STATUS_OK, r.status_code
        except Exception:
            return False, None

    def get_wayback(self, url):
        self.api_call(lambda: None)
        try:
            return WaybackMachineSaveAPI(url).save()
        except Exception:
            return None

    def add_archive(self, item, archive_url, original_url):
        claim = pywikibot.Claim(self.site, "P1065")
        claim.setTarget(archive_url)
        self.api_call(item.addClaim, claim,
                      summary=f"Archiving dead reference: {original_url} (SonalBot)")
        self.archived += 1
        logger.info(f"Archived: {item.id}")

    def process_item(self, item):
        for claim in item.claims.get("P854", []):
            url = claim.getTarget()
            if not url:
                continue
            self.checked += 1
            alive, status = self.check_url(url)
            if not alive:
                archive = self.get_wayback(url)
                if archive:
                    self.add_archive(item, archive, url)

    def run(self, limit=500):
        logger.info(f"Starting. Limit: {limit}")

        # Use recent changes to find items with P854 edits
        # This avoids SPARQL timeout issues
        count = 0
        for change in self.site.recentchanges(
            start=time.strftime('%Y%m%d%H%M%S'),
            end=(time.time() - 86400),  # Last 24 hours
            changetype='edit'
        ):
            if count >= limit:
                break
            try:
                item = pywikibot.ItemPage(self.site, change['title'])
                item.get()
                if 'P854' in item.claims:
                    self.process_item(item)
                    count += 1
            except Exception as e:
                logger.debug(f"Skip {change['title']}: {e}")

        logger.info(f"Done. Checked: {self.checked}, Archived: {self.archived}")
        return self.checked, self.archived


if __name__ == "__main__":
    DeadLinkArchiver().run(limit=500)
