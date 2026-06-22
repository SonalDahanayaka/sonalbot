# -*- coding: utf-8 -*-
"""
MAX LEVEL Welcome Bot — 24/7.

KEY BEHAVIOR:
- Only welcomes users AFTER their FIRST edit
- Welcomes EXACTLY ONCE — never again
- Forgets old users automatically (no memory bloat)
- Checks talk page to confirm not already welcomed

Auto-scales: 60/min → 500/min when flag detected.
"""

import time
import pywikibot
from sonalbot.core.bot import SonalBot
from sonalbot.core.logger import get_logger

logger = get_logger(__name__)


class WelcomeBot(SonalBot):
    """MAX LEVEL welcome bot. One welcome per user. Forgets old users."""

    CHECK_INTERVAL = 15  # Seconds between checks
    TEMPLATE = "{{subst:WelcomeSonalBot|welcominguser=SonalDahanayaka|1=~~~~}}"

    def __init__(self):
        super().__init__()
        self.welcomed_count = 0
        # Only track users in CURRENT session — old users are forgotten
        self._session_welcomed = set()

    def _is_already_welcomed(self, username):
        """
        Check if user was already welcomed.
        Looks at their talk page — NOT memory. So old users are truly forgotten.
        """
        # Fast check: in-memory session cache
        if username in self._session_welcomed:
            return True

        # Real check: look at talk page (this is the source of truth)
        try:
            talk = pywikibot.Page(self.site, f"User talk:{username}")
            if talk.exists() and "WelcomeSonalBot" in talk.text:
                # Cache for this session only
                self._session_welcomed.add(username)
                return True
        except Exception:
            pass

        return False

    def _has_first_edit(self, username):
        """Check if user has made at least ONE edit."""
        try:
            user = pywikibot.User(self.site, username)
            return user.editCount() > 0
        except Exception:
            return False

    def _welcome_user(self, username):
        """Post welcome message."""
        talk = pywikibot.Page(self.site, f"User talk:{username}")

        if self.save_page(talk, self.TEMPLATE, "Welcome to Wikidata! (SonalBot)"):
            self._session_welcomed.add(username)
            self.welcomed_count += 1
            logger.info(f"✅ Welcomed: {username} (total: {self.welcomed_count})")
            return True
        return False

    def _process_new_users(self):
        """
        Process recent new users.
        Only welcomes those with FIRST edit and not already welcomed.
        """
        try:
            # Get recent new user registrations (last check window)
            for logentry in self.site.logevents(logtype="newusers", total=50):
                username = logentry["user"]

                # Skip if already welcomed (checks talk page)
                if self._is_already_welcomed(username):
                    continue

                # CRITICAL: Only welcome AFTER first edit
                if not self._has_first_edit(username):
                    logger.debug(f"⏳ {username} has not edited yet — skipping")
                    continue

                # Welcome them!
                self._welcome_user(username)

                # Small delay between welcomes (rate limiter handles max)
                time.sleep(0.12)

        except Exception as e:
            logger.error(f"Cycle error: {e}")

    def run(self):
        """Run welcome bot continuously (24/7)."""
        logger.info("🟢 WelcomeBot started — 24/7")
        logger.info("Behavior: Welcome ONCE after FIRST edit. Forget old users.")

        while True:
            self._process_new_users()
            logger.debug(f"Sleeping {self.CHECK_INTERVAL}s before next check")
            time.sleep(self.CHECK_INTERVAL)


if __name__ == "__main__":
    WelcomeBot().run()
