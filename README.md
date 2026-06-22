# SonalBot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Toolforge](https://img.shields.io/badge/Toolforge-sonalbot-blue)](https://toolsadmin.wikimedia.org/tools/id/sonalbot)

A Wikidata maintenance bot that improves data quality and welcomes new contributors.

## What It Does

SonalBot runs two independent tasks on Wikidata:

| Task | Description | Schedule | Rate |
|------|-------------|----------|------|
| **Dead Link Archiver** | Checks P854 URLs, archives dead ones to P1065 via Wayback Machine | Daily 06:00 UTC | Auto: 1/sec → 8.33/sec |
| **Welcome Bot** | Welcomes new users **once** after their **first edit** | 24/7 continuous | Auto: 1/sec → 8.33/sec |

Both tasks auto-scale to MAX LEVEL when bot flag is detected. No code changes needed.

## Welcome Bot Behavior

- Monitors new user registrations
- **Waits for first edit** before welcoming
- **Welcomes exactly once** — never again
- Forgets old users automatically (no memory bloat)
- Uses custom template: `Template:WelcomeSonalBot`

## Installation

```bash
git clone https://github.com/SonalDahanayaka/sonalbot.git
cd sonalbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

```bash
cp config/user-config.example.py config/user-config.py
# Edit config/user-config.py with your credentials
```

## Usage

```bash
# Run welcome bot (24/7)
python scripts/start_welcome.py

# Run dead link archiver (once)
python scripts/run_dead_links.py --limit 50
```

## Auto-Scale Rate

| Phase | Rate | Per Minute | Detected By |
|-------|------|-----------|-------------|
| Testing (no bot flag) | 1/sec | 60 | Auto |
| MAX LEVEL (bot flag) | 8.33/sec | 500 | Auto (no restart needed) |

## License

[MIT](LICENSE)
