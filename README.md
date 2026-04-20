# Subscription Tracker

A web application built with Flask for tracking personal subscriptions, monitoring spending, and educating users about subscription dark patterns and cancellation tactics. Developed as a Year 3 dissertation project.


## Overview

The app helps users take control of their subscriptions by providing a central dashboard to manage costs, view upcoming bills, analyse spending trends, and learn how to recognise and cancel subscriptions that use deceptive UI patterns.

## Features

### Authentication
- User registration with email validation and duplicate username/email checks
- Bcrypt password hashing
- Session-based login/logout via Flask-Login
- CSRF protection on all forms via Flask-WTF

### Subscription Management (CRUD)
- Add, edit, and delete subscriptions
- Fields: service name, cost, billing cycle (weekly/monthly/yearly), category, next payment date, cancellation URL, notes
- Active/inactive toggle per subscription
- Ownership enforcement — users can only modify their own subscriptions

### Dashboard
- Summary cards: total monthly cost, active subscription count, budget remaining
- Monthly budget setting with a visual progress bar
- Full filtering and sorting: search by name, filter by category/status, sort by name/cost/billing cycle
- Date-range filtering by payment month/year (exact or "up to" mode)
- Cost cap filter
- Filtered summary stats showing cost share vs. total

### Analytics
- Spending breakdown by category
- Top 5 most expensive subscriptions
- Total monthly cost, average cost, most expensive and cheapest subscriptions
- Chart data exposed to the frontend (category pie/bar and top-5 breakdown)

### Upcoming Bills
- Ordered list of upcoming payments with urgency banding: overdue, urgent (≤7 days), soon (≤14 days), upcoming (≤30 days), later
- Running totals for payments due within 7, 14, and 30 days

### Education — Cancellation Guides
- Database-backed guides covering step-by-step cancellation instructions per service
- Difficulty rating (easy/medium/hard), tips, dark pattern warnings, and direct cancellation URL
- Searchable/browsable list with individual detail pages
- Steps parsed and presented as numbered lists

### Education — Dark Patterns
- Catalogue of dark patterns grouped by category and linked cognitive bias
- Each pattern includes: description, real-world example, how to spot it, how to protect yourself, source citation, and optional image
- Search endpoint (JSON) for live pattern lookup
- Browse by category or cognitive bias

---

## Project Structure

```
subscription-tracker/
├── run.py                    # Application entry point
├── config.py                 # Config (SECRET_KEY, DB URI via .env)
├── requirements.txt
├── app/
│   ├── __init__.py           # App factory, blueprint registration
│   ├── extensions.py         # db, bcrypt, login_manager, csrf
│   ├── models.py             # SQLAlchemy models
│   ├── auth/                 # /auth blueprint (register, login, logout)
│   ├── main/                 # / blueprint (dashboard, analytics, upcoming bills)
│   ├── subscriptions/        # /subscriptions blueprint (add, edit, delete)
│   ├── education/            # /education blueprint (cancellation guides, dark patterns)
│   ├── templates/            # Jinja2 templates per blueprint
│   └── static/               # CSS, JS, images
└── data_seeding/
    ├── scripts/
    │   ├── seed_data.py          # General seed data
    │   ├── seed_cancellation.py  # Cancellation guide seed
    │   └── seed_dark_patterns.py # Dark patterns seed
    ├── cancellation_data.csv
    └── dark_patterns_data.xlsx
```

---

## Data Models

| Model | Purpose |
|---|---|
| `User` | Account with username, email, hashed password, monthly budget |
| `Subscription` | User-owned subscription with cost, billing cycle, category, active flag |
| `CancellationGuide` | Step-by-step cancellation instructions per service |
| `DarkPattern` | Individual dark pattern with category, cognitive bias, examples |
| `DarkPatternCategory` | Category grouping for dark patterns |
| `CognitiveBias` | Psychological bias linked to dark patterns |

The `Subscription.monthly_cost` property normalises weekly and yearly costs to a monthly equivalent for consistent comparisons.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3.1 |
| ORM | Flask-SQLAlchemy 3.1 |
| Database | SQLite (default) |
| Auth | Flask-Login, Flask-Bcrypt |
| Forms/CSRF | Flask-WTF |
| Email validation | email-validator |
| Config | python-dotenv |
| Data seeding | openpyxl (Excel), csv |

---

## Setup

1. **Clone and create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**

   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key
   SQLALCHEMY_DATABASE_URI=sqlite:///subscriptions.db
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **(Optional) Seed the database**
   ```bash
   python data_seeding/scripts/seed_data.py
   python data_seeding/scripts/seed_cancellation.py
   python data_seeding/scripts/seed_dark_patterns.py
   ```

---

## Development Stages

| Stage | Description |
|---|---|
| 1 | Project foundation — Flask app factory, blueprints, SQLAlchemy models |
| 2 | Authentication, subscription CRUD, dashboard with filtering |
| 3 | Analytics page and upcoming bills view |
| 4 | Cancellation guide and dark patterns education section |
| 5 | UI polish and navbar icons |
| Fixes | Active status toggle, duplicate username check on registration, portable seed scripts |