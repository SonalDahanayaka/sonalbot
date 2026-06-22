#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup cron jobs for SonalBot.
"""

import os

CRON_CONTENT = """# SonalBot Dead Link Archiver
# Runs daily at 06:00 UTC
0 6 * * * /data/project/sonalbot/venv/bin/python /data/project/sonalbot/repo/scripts/run_dead_links.py >> /data/project/sonalbot/logs/dead_links.log 2>&1
"""


def install():
    cron_file = "/data/project/sonalbot/cron/dead_links.cron"
    os.makedirs(os.path.dirname(cron_file), exist_ok=True)
    with open(cron_file, "w") as f:
        f.write(CRON_CONTENT)
    print(f"Cron file written to: {cron_file}")
    print("Install with: crontab /data/project/sonalbot/cron/dead_links.cron")


if __name__ == "__main__":
    install()
