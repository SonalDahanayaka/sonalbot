#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entry point: Run Dead Link Archiver (daily)
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sonalbot.tasks.dead_link_archiver import DeadLinkArchiver

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run dead link archiver")
    parser.add_argument("--limit", type=int, default=500, help="Max items to check")
    args = parser.parse_args()

    DeadLinkArchiver().run(limit=args.limit)
