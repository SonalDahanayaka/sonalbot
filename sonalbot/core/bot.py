# -*- coding: utf-8 -*-
"""
MAX LEVEL base bot — auto-scales to API ceiling.
"""

import time
import pywikibot
from sonalbot.core.rate_limiter import init_limiter
from sonalbot.core.logger import get_logger

logger = get_logger(__name__)


class SonalBot:
    """MAX LEVEL bot — auto-detects flag, auto-scales rate."""

    def __init__(self):
        self.site = pywikibot.Site("wikidata", "wikidata")
        self.site.login()
        from sonalbot.core.rate_limiter import limiter
        if limiter is None:
            init_limiter(self.site)
        self._log_status()
        logger.info("Bot initialized")

    def _log_status(self):
        from sonalbot.core.rate_limiter import limiter
        if limiter and limiter._check_bot_flag():
            logger.info("🚀 MAX LEVEL: 8.33 req/sec (500/min)")
        else:
            logger.info("⏳ SAFE MODE: 1 req/sec (60/min) — waiting for bot flag")

    def api_call(self, func, *args, **kwargs):
        from sonalbot.core.rate_limiter import limiter
        if limiter:
            limiter.acquire()
        return func(*args, **kwargs)

    def save_page(self, page, text, summary):
        for attempt in range(3):
            try:
                from sonalbot.core.rate_limiter import limiter
                if limiter:
                    limiter.acquire()
                page.text = text
                page.save(summary=summary, minor=False, tags="SonalBot")
                logger.info(f"Saved: {page.title()}")
                return True
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(5 * (attempt + 1))
        return False
