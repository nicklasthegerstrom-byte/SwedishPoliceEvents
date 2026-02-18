# Nick's Police Monitor 2.0

A headless newsroom monitoring system for Swedish police incidents.

Built in Python to run 24/7, store historical data, filter by severity,
and send notifications when new serious incidents occur.

Designed for editorial decision-making under real-world conditions.

---

## What It Does

The system continuously fetches incident data from the Swedish Police public API and:

- Stores all events in a local SQLite database
- Assigns each event type a seriousness score (1–10)
- Filters events based on configurable minimum severity
- Sends notifications (Discord / Slack) for new serious events
- Avoids duplicate notifications via a notified-events table
- Logs errors and unknown event types
- Runs safely in an infinite loop without crashing

This is essentially a lightweight editorial surveillance engine for real-time blue-light news.

---

## Core Design Principles

- Never crash the loop
- Never send duplicate notifications
- Fail safe rather than fail silent
- Log unexpected behavior
- Keep the system observable and debuggable

---

## Architecture Overview

polisprojekt/
- main.py               → Infinite loop entry point
- config.py             → Environment variables and paths
- services/
    - pipeline.py       → Orchestrates fetch → filter → notify
    - notify.py         → Slack / Discord logic + dedupe
    - database.py       → SQLite persistence + notified table
    - logger.py         → Rotating file logging
    - sorting.py        → Serious event filtering
- data/
    - api_fetch.py      → API calls + retry/backoff logic
    - scoring.py        → Event severity mapping
- model/
    - event_model.py    → Event model + formatting
- tests/                → Pytest-based test suite

Database:
- SQLite
- events table (history)
- notified table (deduplication)

Logging:
- Rotating file handler
- Daily log rotation
- Error + anomaly visibility

---

## Severity Model

Each event type is mapped to a seriousness score (1–10).

Examples:
- Murder: 10
- Explosion: 9
- Shooting: 9
- Robbery: 7
- Minor disturbance: 3

Unknown event types:
- Receive a high default score (fail-safe design)
- Are logged for review

---

## Reliability Features

- Request timeout handling
- Retry logic with backoff
- Graceful handling of:
  - Network errors
  - HTTP errors
  - Invalid JSON responses
- Loop-level exception safety
- Persistent deduplication of notifications

The system is designed to survive unstable networks and API irregularities.

---

## Testing

The project includes pytest-based tests covering:

- Network failures
- HTTP errors
- Invalid JSON
- Retry behavior
- Notification success/failure handling
- Deduplication logic
- Severity filtering

---

## Intended Use

This tool is built for newsroom environments where:

- Time matters
- Noise must be filtered
- Serious events must not be missed
- Automation supports editorial judgment

It is not a web app.
It is an autonomous monitoring service.

---

Built for real-world editorial workflows.