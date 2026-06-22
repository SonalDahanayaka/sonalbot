# -*- coding: utf-8 -*-
"""
URL checking utilities.
"""

import requests


def check_url_alive(url, timeout=10):
    """Check if URL returns success status."""
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True,
                          headers={'User-Agent': 'SonalBot/1.0 (Wikidata bot)'})
        return r.status_code < 400, r.status_code
    except requests.RequestException:
        return False, None
