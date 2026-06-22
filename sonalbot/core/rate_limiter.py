# -*- coding: utf-8 -*-
"""
Auto-scaling rate limiter — MAX LEVEL.
No flag: 1 req/sec (safe testing)
With flag: 8.33 req/sec (500/min exact max)
"""

import time
from threading import Lock


class RateLimiter:
    """MAX LEVEL rate limiter. Auto-scales to API ceiling."""

    SAFE_RATE = 1.0
    SAFE_BURST = 2
    MAX_RATE = 8.333333
    MAX_BURST = 10

    def __init__(self, site=None):
        self.site = site
        self.lock = Lock()
        self.tokens = self.SAFE_BURST
        self.last_update = time.time()
        self._has_flag = None
        self._flag_checked = 0
        self._rate_logged = False

    def _check_bot_flag(self):
        now = time.time()
        if self._has_flag is None or (now - self._flag_checked) > 60:
            self._has_flag = False
            if self.site:
                try:
                    user = self.site.users([self.site.username()])
                    user_info = list(user)[0]
                    self._has_flag = 'bot' in user_info.get('groups', [])
                except Exception:
                    pass
            self._flag_checked = now
        return self._has_flag

    def _get_rate(self):
        return self.MAX_RATE if self._check_bot_flag() else self.SAFE_RATE

    def _get_burst(self):
        return self.MAX_BURST if self._check_bot_flag() else self.SAFE_BURST

    def acquire(self):
        with self.lock:
            rate = self._get_rate()
            burst = self._get_burst()
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(burst, self.tokens + elapsed * rate)
            self.last_update = now

            if self.tokens < 1:
                time.sleep((1 - self.tokens) / rate)
                self.tokens = 0
            else:
                self.tokens -= 1

            if not self._rate_logged and self._check_bot_flag():
                self._rate_logged = True
                print(f"🚀 MAX LEVEL: {rate:.2f} req/sec = {int(rate*60)}/min")


limiter = None


def init_limiter(site):
    global limiter
    limiter = RateLimiter(site)
    return limiter
