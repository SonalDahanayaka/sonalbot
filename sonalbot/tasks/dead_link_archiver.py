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

    def __init__(self, log_dir: str = None):
        super().__init__(log_dir=log_dir)
        self.checked = 0
        self.archived = 0
        self.dead = 0
        self.errors = 0
        self.skipped = 0

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

    def is_already_archived(self, claim, url):
        """Check if THIS CLAIM already has a reference with P1065 for this URL."""
        for source in claim.sources:
            p854_list = source.get("P854", [])
            if not p854_list:
                continue
            if p854_list[0].getTarget() == url and "P1065" in source:
                return True
        return False

    def add_archive_to_reference(self, claim, source, archive_url, original_url):
        """Add P1065 as new reference on same claim."""
        try:
            p1065 = pywikibot.Claim(self.site, 'P1065')
            p1065.setTarget(archive_url)
            
            claim.addSource(p1065, summary=f"Adding archive for dead reference: {original_url} (SonalBot)")
            
            self.archived += 1
            logger.info(f"Added archive reference: {original_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add archive: {e}")
            self.errors += 1
            return False

    def process_item(self, item):
        """Check all references on all claims for P854 URLs."""
        for prop, claims in item.claims.items():
            for claim in claims:
                for source in claim.sources:
                    p854_claims = source.get("P854", [])
                    if not p854_claims:
                        continue
                    
                    url = p854_claims[0].getTarget()
                    if not url:
                        continue
                    
                    # Check if THIS SPECIFIC claim already has archive
                    if self.is_already_archived(claim, url):
                        logger.info(f"Already archived on this claim: {url}")
                        self.skipped += 1
                        continue
                    
                    self.checked += 1
                    alive, status = self.check_url(url)
                    if not alive:
                        self.dead += 1
                        archive = self.get_wayback(url)
                        if archive:
                            self.add_archive_to_reference(claim, source, archive, url)
                    else:
                        logger.info(f"Link alive: {url}")

    def run(self, limit=500):
        logger.info(f"Starting. Limit: {limit}")

        query = """
        SELECT DISTINCT ?item WHERE {
          ?item ?p ?stmt.
          ?stmt prov:wasDerivedFrom ?ref.
          ?ref pr:P854 ?url.
          FILTER NOT EXISTS {
            ?stmt prov:wasDerivedFrom ?anyRef.
            ?anyRef pr:P1065 ?archive.
          }
          FILTER (STRSTARTS(STR(?item), "http://www.wikidata.org/entity/Q"))
        }
        LIMIT %d
        """ % limit

        try:
            from pywikibot.data.sparql import SparqlQuery
            results = SparqlQuery().select(query, timeout=120)
            logger.info(f"SPARQL: {len(results)} items")
        except Exception as e:
            logger.error(f"SPARQL failed: {e}")
            results = []

        for row in results:
            item_id = None
            try:
                item_id = row['item'].split('/')[-1]
                item = pywikibot.ItemPage(self.site, item_id)
                item.get()
                self.process_item(item)
            except Exception as e:
                logger.error(f"Error {item_id}: {e}")
                self.errors += 1

        logger.info(f"Done. Checked: {self.checked}, Dead: {self.dead}, Archived: {self.archived}, Skipped: {self.skipped}")
        return {
            'checked': self.checked,
            'dead': self.dead,
            'archived': self.archived,
            'skipped': self.skipped,
            'errors': self.errors,
            'elapsed_seconds': 0,
        }


if __name__ == "__main__":
    DeadLinkArchiver().run(limit=500)
