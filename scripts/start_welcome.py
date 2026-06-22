#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entry point: Start Welcome Bot (24/7)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sonalbot.tasks.welcome_bot import WelcomeBot

if __name__ == "__main__":
    WelcomeBot().run()
