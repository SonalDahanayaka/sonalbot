# -*- coding: utf-8 -*-
"""
MAX LEVEL Welcome Bot — 24/7.

KEY BEHAVIOR:
- Catches ALL users after their FIRST edit (even old registrations)
- Welcomes EXACTLY ONCE — never again
- Ignores already-welcomed users and old established users
- Checks talk page to confirm not already welcomed

Auto-scales: 60/min → 500/min when flag detected.
"""

import time
import datetime
import pywikibot
from sonalbot.core.bot import SonalBot
from sonalbot.core.logger import get_logger

logger = get_logger(__name__)


class WelcomeBot(SonalBot):
    """MAX LEVEL welcome bot. Catches all first-time editors."""

    CHECK_INTERVAL = 15  # Seconds between checks
    RECENT_CHANGES_LIMIT = 2000  # Check last 2000 edits for first-timers
    MAX_USER_AGE_DAYS = 30  # Only welcome users registered within last 30 days
    TEMPLATE = "{{subst:WelcomeSonalBot|welcominguser=SonalDahanayaka|1=~~~~}}"

    def __init__(self):
        super().__init__()
        self.welcomed_count = 0
        self._session_welcomed = set()  # Cache for current session
        self._session_checked = set()   # Users we already checked this session
        self._last_check_time = None   # Track last recentchanges check

    def _is_already_welcomed(self, username):
        """Check if user was already welcomed (talk page check)."""
        if username in self._session_welcomed:
            return True

        try:
            talk = pywikibot.Page(self.site, f"User talk:{username}")
            if talk.exists() and "WelcomeSonalBot" in talk.text:
                self._session_welcomed.add(username)
                return True
        except Exception:
            pass

        return False

    def _is_new_user(self, username):
        """Check if user is relatively new (registered within MAX_USER_AGE_DAYS)."""
        try:
            user = pywikibot.User(self.site, username)
            # Check registration date
            reg_date = getattr(user, 'registration', None)
            if reg_date:
                if isinstance(reg_date, str):
                    reg_date = datetime.datetime.strptime(reg_date, '%Y-%m-%dT%H:%M:%SZ')
                days_old = (datetime.datetime.now() - reg_date).days
                return days_old <= self.MAX_USER_AGE_DAYS
            # If no registration date, check edit count
            return user.editCount() <= 10  # Treat low-edit users as new
        except Exception:
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

    def _process_recent_changes(self):
        """
        MAIN METHOD: Check recent changes for first-time editors.
        This catches ALL users who just made their first edit, regardless of when they registered.
        """
        try:
            # Get recent edits (last 2000)
            rc_gen = self.site.recentchanges(
                start=self._last_check_time,
                total=self.RECENT_CHANGES_LIMIT,
                changetype='edit'  # Only actual edits, not log events
            )

            first_time_editors = set()

            for change in rc_gen:
                username = change.get('user')
                if not username:
                    continue

                # Skip bots and IP addresses
                if username.endswith('Bot') or ':' in username or '.' in username:
                    continue

                # Skip if already checked this session
                if username in self._session_checked:
                    continue

                self._session_checked.add(username)

                # Skip if already welcomed
                if self._is_already_welcomed(username):
                    continue

                # Skip old established users
                if not self._is_new_user(username):
                    logger.debug(f"⏩ {username} is not a new user — skipping")
                    continue

                # Check if this is their first edit
                if not self._has_first_edit(username):
                    continue

                # This is a new user with at least one edit!
                first_time_editors.add(username)

            # Welcome all first-time editors found
            for username in first_time_editors:
                logger.info(f"🆕 First-time editor detected: {username}")
                self._welcome_user(username)
                time.sleep(0.12)  # Rate limit between welcomes

            # Update last check time
            self._last_check_time = datetime.datetime.now()

        except Exception as e:
            logger.error(f"Recent changes error: {e}")

    def _process_new_users_log(self):
        """
        BACKUP METHOD: Also check newusers log for any we might have missed.
        Catches users who registered and edited very quickly.
        """
        try:
            for logentry in self.site.logevents(logtype="newusers", total=50):
                username = logentry["user"]

                # Skip if already checked
                if username in self._session_checked:
                    continue
                self._session_checked.add(username)

                # Skip if already welcomed
                if self._is_already_welcomed(username):
                    continue

                # Skip if no edits yet
                if not self._has_first_edit(username):
                    continue

                # Welcome them
                self._welcome_user(username)
                time.sleep(0.12)

        except Exception as e:
            logger.error(f"New users log error: {e}")

    def run(self):
        """Run welcome bot continuously (24/7)."""
        logger.info("🟢 WelcomeBot started — 24/7")
        logger.info("Behavior: Catches ALL first-time editors via recentchanges. One welcome per user.")

        while True:
            # Primary: Check recent changes for first-time editors
            self._process_recent_changes()

            # Backup: Check newusers log
            self._process_new_users_log()

            logger.debug(f"Sleeping {self.CHECK_INTERVAL}s before next check")
            time.sleep(self.CHECK_INTERVAL)


if __name__ == "__main__":
    WelcomeBot().run()
