# -*- coding: utf-8 -*-
"""
Wayback Machine utilities.
"""

from waybackpy import WaybackMachineSaveAPI


def get_archive_url(url):
    """Get Wayback Machine archive URL."""
    try:
        return WaybackMachineSaveAPI(url).save()
    except Exception:
        return None
