# pi-house

A self-hosted home management app designed to run on a Raspberry Pi on your local network. Built with Flask and PostgreSQL, deployed via Docker with a GitHub Actions CI/CD pipeline.

## Features

- **House Expense Tracking** — log expenses by project and retailer, with a dashboard showing spending by category, project, and month (Chart.js)
- **Project Management** — organize expenses under house projects, track totals per project
- **Retailer Management** — maintain a reusable list of retailers with soft-delete
- **To-Do Lists** — household task tracking
- **Tile & Table Views** — toggle between views on expenses and projects (preference saved to localStorage)
- **Filters** — filter by project, year, month, quarter, and category
- **Authentication** — Flask-Login with user profile management (username, email, password)
- **Mobile Responsive** — works well on phones and tablets

## Tech Stack

- **Backend**: Flask + PostgreSQL
- **Frontend**: Jinja2 templates, Bootstrap, Chart.js
- **Deployment**: Docker + Docker Compose on Raspberry Pi
- **CI/CD**: GitHub Actions (runs tests on PRs, deploys to Pi on merge to main)
- **Remote Access**: Tailscale

## Getting Started

### Prerequisites

- Raspberry Pi 4 or 5 running Raspberry Pi OS (64-bit)
- Docker and Docker Compose installed on the Pi
- Python 3.11+ (for local development)
- A GitHub account (for CI/CD)

### Local Development

1. Clone the repo:
   ```bash
   git clone https://github.com/leetroyjenkins/pi-house.git
   cd pi-house
   ```

2. Copy the example env file and fill in your values:
   ```bash
   cp .env.example .env
   ```

3. Start the app with Docker Compose:
   ```bash
   docker compose up
   ```

4. Initialize the database and create your first user:
   ```bash
   docker compose exec web flask init-db
   docker compose exec web flask create-user
   ```

5. Visit `http://localhost:5000`

### Deploying to a Raspberry Pi

See [`docs/DEPLOYMENT_PLAN.md`](docs/DEPLOYMENT_PLAN.md) for a full walkthrough of setting up the Pi, configuring Docker, and wiring up the GitHub Actions deployment pipeline.

## Project Structure

```
pi-house/
├── app/
│   ├── routes/         # Flask blueprints (auth, house, todos)
│   ├── templates/      # Jinja2 HTML templates
│   ├── models.py       # SQLAlchemy models
│   └── forms.py        # WTForms
├── docs/               # Deployment and setup guides
├── migrations/         # Database migrations
├── tests/
├── .github/workflows/  # CI/CD pipeline
├── docker-compose.yml
└── Dockerfile
```

## Related

- [pi-budget](https://github.com/leetroyjenkins/pi-budget) — A zero-based budgeting app for Raspberry Pi (in development). Uses the same deployment architecture as this project.
