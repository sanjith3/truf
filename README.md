# TurfSpot - Sports Booking Platform

A premium sports booking platform for discovery and scheduling turfs (football/cricket) across Tamil Nadu and Kerala.

## Features
- Instant discovery of available turfs
- Real-time booking system
- User & Owner Dashboards
- Multi-language support (English, Tamil, Malayalam)

## Tech Stack
- Django (Backend)
- Tailwind CSS (Frontend)
- SQLite (Development Database)

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment:
   - Windows: `.\.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the server:
   ```bash
   python manage.py runserver
   ```
