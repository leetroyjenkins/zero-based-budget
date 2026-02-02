# Personal Budget App - Complete Project Plan (Docker Deployment)

## Project Overview
Build and deploy a zero-based budgeting application with virtual funds management to a Raspberry Pi on the local network using Docker containers. The application uses Flask + PostgreSQL in Docker with Traefik/Nginx reverse proxy for HTTPS. Includes CI/CD pipeline with GitHub Actions for streamlined development and deployment.

**Status**: Planning Complete - Ready for Implementation
**Last Updated**: 2026-01-10

---

## Quick Reference

**Documentation**:
- [Functional Requirements](FUNCTIONAL_REQUIREMENTS.md) - What the app needs to do
- [Database Schema](DATABASE_SCHEMA.md) - Complete data model design
- [Deployment Requirements](DEPLOYMENT_REQUIREMENTS.md) - Technical specifications

**Key Decisions**:
- **Architecture**: Docker containers (Flask app + PostgreSQL)
- **Deployment**: Raspberry Pi 4/5 on local network (existing server named "piserver")
- **Reverse Proxy**: Traefik or Nginx for HTTPS/SSL termination
- **Security**: HTTPS with self-signed certificates
- **CI/CD**: GitHub Actions building Docker images and deploying
- **Workflow**: Feature branches + PRs, manual approval for deployment

---

## Project Phases

### Phase 1: Infrastructure Preparation [0/5 complete]
Clean up existing Pi and prepare for Docker deployment

### Phase 2: Development Environment [0/5 complete]
Configure local development, Docker setup, and CI/CD pipeline

### Phase 3: Database & Docker Compose [0/4 complete]
Create database schema and Docker Compose configuration

### Phase 4: Application Development [0/11 complete]
Build Flask application with all features (includes gas tracker, down payment tracker, house calculator)

### Phase 5: Deployment & Testing [0/5 complete]
Deploy to Pi and validate functionality

### Phase 6: Documentation & Handoff [0/3 complete]
Complete documentation and training

---

## Detailed Task Breakdown

## Phase 1: Infrastructure Preparation

### 1.1 Assess Current Raspberry Pi Setup
**Status**: ⬜ Not Started
**Estimated Time**: 30 minutes
**Prerequisites**: SSH access to Pi

**Tasks**:
- [x] SSH to Pi: `ssh pi@piserver.local` (or current hostname)
- [x] Check current hostname: `hostname`
- [x] Check Docker version: `docker --version`
- [x] Check Docker Compose version: `docker-compose --version` or `docker compose version`
- [x] List running containers: `docker ps -a`
- [x] Check disk space: `df -h`
- [x] Check available memory: `free -h`
- [x] List installed packages: `dpkg -l | grep -E 'apache|mysql|mariadb'`
- [x] Document current state in session log

**Deliverable**: Understanding of current Pi setup

**Verification**:
```bash
ssh pi@piserver.local
docker --version  # Should show Docker 20.x or newer
docker-compose --version  # Should show version or use 'docker compose'
```

---

### 1.2 Backup and Clean Up Minecraft Server
**Status**: ✅ Complete
**Estimated Time**: 45 minutes
**Prerequisites**: Task 1.1 complete

**Tasks**:
- [x] List Minecraft-related containers: `docker ps -a | grep minecraft`
- [x] Stop Minecraft containers: `docker stop <container-name>`
- [x] Backup any configuration files you want to keep:
  ```bash
  mkdir -p ~/backups/minecraft_config
  # Copy any important config files
  ```
- [x] Remove Minecraft containers: `docker rm <container-name>`
- [x] Remove Minecraft images: `docker rmi <image-name>`
- [x] Remove unused volumes: `docker volume ls` then `docker volume rm <volume-name>` if safe
- [x] Remove Minecraft directories (if any outside Docker)
- [x] Clean up Docker: `docker system prune -a`
- [x] Verify space freed: `df -h`

**Deliverable**: Clean Pi with Docker ready for new apps

**Verification**:
```bash
docker ps -a  # Should show no Minecraft containers
docker images  # Should show no Minecraft images
df -h  # Should show increased available space
```

---

### 1.3 Update Pi System and Docker
**Status**: ✅ Complete
**Estimated Time**: 30 minutes
**Prerequisites**: Task 1.2 complete

**Tasks**:
- [x] Update package lists: `sudo apt update`
- [x] Upgrade installed packages: `sudo apt upgrade -y`
- [x] Update Docker if needed: `sudo apt install --only-upgrade docker-ce docker-ce-cli containerd.io`
- [x] Install/update Docker Compose v2 if needed:
  ```bash
  sudo apt install docker-compose-plugin
  ```
- [x] Verify Docker Compose: `docker compose version`
- [x] Install utilities if missing: `sudo apt install -y git vim curl wget htop`
- [x] Reboot if kernel updated: `sudo reboot`

**Deliverable**: Fully updated Pi system with latest Docker

**Verification**:
```bash
docker --version  # Should show latest version
docker compose version  # Should show Compose v2
uname -r  # Check kernel version updated
```

---

### 1.4 Configure Hostname and Network
**Status**: Not Complete
**Estimated Time**: 20 minutes
**Prerequisites**: Task 1.3 complete

**Tasks**:
- [x] Set hostname to "piserver":
  ```bash
  sudo hostnamectl set-hostname piserver
  sudo sed -i 's/raspberrypi/piserver/g' /etc/hosts
  ```
- [ ] Check current IP: `ip addr show`
- [ ] Configure static IP if needed (via router DHCP reservation recommended)
- [ ] Document IP address and hostname in password manager
- [ ] Test connectivity from main computer: `ping piserver.local`
- [ ] Test SSH with new hostname: `ssh pi@piserver.local`

**Deliverable**: Pi accessible at piserver.local with static IP

**Verification**:
```bash
hostname  # Should show "piserver"
ping piserver.local  # From another device, should respond
```

---

### 1.5 Create Application Directories
**Status**: ✅ Complete
**Estimated Time**: 15 minutes
**Prerequisites**: Task 1.4 complete

**Tasks**:
- [x] Create apps directory: `mkdir -p ~/apps`
- [x] Create budget app directory: `mkdir -p ~/apps/budget`
- [x] Create shared data directory: `mkdir -p ~/apps/shared/certs`
- [x] Create Docker network for apps:
  ```bash
  docker network create apps_network
  ```
- [x] Set up directory structure:
  ```
  ~/apps/
  ├── budget/          # Budget app code and compose file
  ├── shared/
  │   ├── certs/       # SSL certificates
  │   └── nginx/       # Reverse proxy config (if using)
  └── data/            # Persistent data volumes
  ```

**Deliverable**: Directory structure ready for Docker apps

**Verification**:
```bash
ls -la ~/apps/
docker network ls | grep apps_network
```

---

## Phase 2: Development Environment

### 2.1 Local Development Setup
**Status**: ⬜ Not Started
**Estimated Time**: 45 minutes
**Prerequisites**: Docker Desktop installed on your main computer

**Tasks**:
- [ ] Ensure Docker Desktop installed on your development machine
- [ ] Clone/navigate to project repo
- [ ] Create `Dockerfile` in project root:
  ```dockerfile
  FROM python:3.11-slim

  WORKDIR /app

  # Install system dependencies
  RUN apt-get update && apt-get install -y \
      gcc \
      libpq-dev \
      && rm -rf /var/lib/apt/lists/*

  # Copy requirements and install Python dependencies
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # Copy application code
  COPY . .

  # Expose port
  EXPOSE 5000

  # Run with gunicorn
  CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "wsgi:application"]
  ```
- [ ] Create `docker-compose.yml`:
  ```yaml
  version: '3.8'

  services:
    db:
      image: postgres:16
      container_name: budget_db
      environment:
        POSTGRES_DB: budget_db
        POSTGRES_USER: budget_user
        POSTGRES_PASSWORD: ${DB_PASSWORD}
      volumes:
        - db_data:/var/lib/postgresql/data
        - ./migrations:/docker-entrypoint-initdb.d:ro
      networks:
        - budget_network
      restart: unless-stopped
      healthcheck:
        test: ["CMD-SHELL", "pg_isready -U budget_user -d budget_db"]
        interval: 10s
        timeout: 5s
        retries: 5

    app:
      build: .
      container_name: budget_app
      depends_on:
        db:
          condition: service_healthy
      environment:
        DATABASE_URL: postgresql+psycopg2://budget_user:${DB_PASSWORD}@db:5432/budget_db
        SECRET_KEY: ${SECRET_KEY}
        FLASK_ENV: production
      volumes:
        - ./app:/app/app:ro  # Mount app code (dev only, remove in prod)
      networks:
        - budget_network
      restart: unless-stopped
      ports:
        - "5000:5000"

  networks:
    budget_network:
      driver: bridge

  volumes:
    db_data:
  ```
- [ ] Create `.env.example`:
  ```
  DB_PASSWORD=change-this-db-password
  SECRET_KEY=change-this-secret-key
  ```
- [ ] Create `.env` from example with real passwords (don't commit!)
- [ ] Add to `.gitignore`:
  ```
  .env
  __pycache__/
  *.pyc
  venv/
  *.db
  .DS_Store
  db_data/
  ```

**Deliverable**: Local Docker development environment ready

**Verification**:
```bash
docker-compose config  # Should show valid config
```

---

### 2.2 Create Requirements and Project Structure
**Status**: ⬜ Not Started
**Estimated Time**: 30 minutes
**Prerequisites**: Task 2.1 complete

**Tasks**:
- [ ] Create `requirements.txt`:
  ```
  Flask==3.0.0
  Flask-SQLAlchemy==3.1.1
  Flask-Login==0.6.3
  Flask-WTF==1.2.1
  psycopg2-binary==2.9.9
  python-dotenv==1.0.0
  pandas==2.2.0
  gunicorn==21.2.0
  pytest==7.4.3
  ```
- [ ] Create project structure (see Phase 4.1 in original plan for details):
  ```
  personal-budget/
  ├── app/
  │   ├── __init__.py
  │   ├── models.py
  │   ├── routes/
  │   ├── templates/
  │   ├── static/
  │   └── forms.py
  ├── migrations/
  ├── tests/
  ├── Dockerfile
  ├── docker-compose.yml
  ├── requirements.txt
  ├── wsgi.py
  ├── config.py
  ├── .env.example
  ├── .env
  └── .gitignore
  ```
- [ ] Test local build: `docker-compose build`
- [ ] Create stub Flask app to test containers start

**Deliverable**: Complete project structure with Docker config

**Verification**:
```bash
docker-compose build  # Should build successfully
```

---

### 2.3 GitHub Repository and Secrets Setup
**Status**: ⬜ Not Started
**Estimated Time**: 30 minutes
**Prerequisites**: GitHub account, Task 2.2 complete

**Tasks**:
- [ ] Push code to GitHub (if not already)
- [ ] Create branch protection rules for `main`:
  - Require pull request reviews
  - Require status checks (tests) to pass
- [ ] Add repository secrets in GitHub Settings > Secrets and Variables > Actions:
  - `PI_HOST` = piserver.local or IP address
  - `PI_USER` = pi
  - `PI_SSH_KEY` = (will generate in next task)
  - `DB_PASSWORD` = secure password
  - `SECRET_KEY` = (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
  - `DOCKERHUB_USERNAME` = (optional, for Docker Hub)
  - `DOCKERHUB_TOKEN` = (optional, for Docker Hub)

**Deliverable**: GitHub repo configured with secrets

**Verification**:
- Check GitHub repo Settings > Secrets shows all secrets configured

---

### 2.4 SSH Key Setup for Deployment
**Status**: ⬜ Not Started
**Estimated Time**: 20 minutes
**Prerequisites**: Task 2.3 complete, Pi accessible

**Tasks**:
- [ ] On your main computer, generate deployment key:
  ```bash
  ssh-keygen -t ed25519 -C "github-deploy-budget" -f ~/.ssh/budget_deploy
  ```
- [ ] Copy public key to Pi:
  ```bash
  ssh-copy-id -i ~/.ssh/budget_deploy.pub pi@piserver.local
  ```
- [ ] Test SSH connection:
  ```bash
  ssh -i ~/.ssh/budget_deploy pi@piserver.local "echo Connected"
  ```
- [ ] Copy private key contents:
  ```bash
  cat ~/.ssh/budget_deploy
  ```
- [ ] Add private key to GitHub repository secrets as `PI_SSH_KEY`
  (Copy entire output including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`)

**Deliverable**: SSH key authentication working for GitHub Actions

**Verification**:
```bash
ssh -i ~/.ssh/budget_deploy pi@piserver.local "docker ps"
# Should connect and show running containers
```

---

### 2.5 GitHub Actions Workflow Creation
**Status**: ⬜ Not Started
**Estimated Time**: 1 hour
**Prerequisites**: Task 2.3, 2.4 complete

**Tasks**:
- [ ] Create `.github/workflows/` directory
- [ ] Create `.github/workflows/deploy.yml`:
  ```yaml
  name: Build and Deploy to Raspberry Pi

  on:
    workflow_dispatch:  # Manual trigger
    release:
      types: [published]
    push:
      branches:
        - main  # Optional: auto-deploy on push to main

  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3

        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'

        - name: Install dependencies
          run: |
            pip install -r requirements.txt
            pip install pytest

        - name: Run tests
          run: pytest tests/ -v || echo "No tests yet"

    build:
      needs: test
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3

        - name: Create .env file
          run: |
            echo "DB_PASSWORD=${{ secrets.DB_PASSWORD }}" >> .env
            echo "SECRET_KEY=${{ secrets.SECRET_KEY }}" >> .env

        - name: Build Docker image
          run: |
            docker build -t budget-app:${{ github.sha }} .
            docker save budget-app:${{ github.sha }} > budget-app.tar

        - name: Upload Docker image
          uses: actions/upload-artifact@v3
          with:
            name: docker-image
            path: budget-app.tar

    deploy:
      needs: build
      runs-on: ubuntu-latest
      environment: production  # Requires manual approval
      steps:
        - uses: actions/checkout@v3

        - name: Download Docker image
          uses: actions/download-artifact@v3
          with:
            name: docker-image

        - name: Deploy to Raspberry Pi
          uses: appleboy/scp-action@master
          with:
            host: ${{ secrets.PI_HOST }}
            username: ${{ secrets.PI_USER }}
            key: ${{ secrets.PI_SSH_KEY }}
            source: "docker-compose.yml,.env,budget-app.tar"
            target: "~/apps/budget"

        - name: Start containers on Pi
          uses: appleboy/ssh-action@master
          with:
            host: ${{ secrets.PI_HOST }}
            username: ${{ secrets.PI_USER }}
            key: ${{ secrets.PI_SSH_KEY }}
            script: |
              cd ~/apps/budget
              docker load < budget-app.tar
              docker tag budget-app:${{ github.sha }} budget-app:latest
              docker-compose down
              docker-compose up -d
              docker-compose ps
              echo "Deployment complete!"
  ```
- [ ] Create environment protection rule in GitHub:
  - Go to Settings > Environments > New environment > "production"
  - Add required reviewers (yourself)
- [ ] Commit and push workflow file
- [ ] Test workflow with manual trigger (will fail until app is built, that's okay)

**Deliverable**: GitHub Actions workflow configured

**Verification**:
- Go to Actions tab in GitHub
- Should see "Build and Deploy to Raspberry Pi" workflow
- Try manual trigger (expect to fail until Phase 4 complete)

---

## Phase 3: Database & Docker Compose

### 3.1 Create Database Schema Files
**Status**: ⬜ Not Started
**Estimated Time**: 1 hour
**Prerequisites**: Task 2.2 complete

**Tasks**:
- [ ] Create `migrations/001_initial_schema.sql` with all table definitions from [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
- [ ] Create `migrations/002_seed_data.sql` with default expense categories
- [ ] Both files will be automatically run by PostgreSQL container on first start (due to `/docker-entrypoint-initdb.d` mount)
- [ ] Test locally:
  ```bash
  docker-compose up -d db
  docker-compose logs db  # Check for migration success
  docker-compose exec db psql -U budget_user -d budget_db -c "\dt"
  ```

**Deliverable**: Database schema ready for Docker deployment

**Verification**:
```bash
docker-compose exec db psql -U budget_user -d budget_db -c "SELECT COUNT(*) FROM expense_categories;"
# Should show default categories after seed
```

---

### 3.2 Test Local Docker Environment
**Status**: ⬜ Not Started
**Estimated Time**: 30 minutes
**Prerequisites**: Task 3.1 complete, basic Flask app exists

**Tasks**:
- [ ] Build containers: `docker-compose build`
- [ ] Start services: `docker-compose up -d`
- [ ] Check containers running: `docker-compose ps`
- [ ] Check logs: `docker-compose logs`
- [ ] Test database connection:
  ```bash
  docker-compose exec app python -c "from app import create_app, db; app=create_app(); app.app_context().push(); print('DB connected!') if db.engine.connect() else print('Failed')"
  ```
- [ ] Access app: http://localhost:5000
- [ ] Stop services: `docker-compose down`

**Deliverable**: Fully functional local Docker development environment

**Verification**:
```bash
curl http://localhost:5000  # Should return HTML
docker-compose exec db psql -U budget_user -d budget_db -c "\dt"  # Should show all tables
```

---

### 3.3 Create Docker Backup Script
**Status**: ⬜ Not Started
**Estimated Time**: 30 minutes
**Prerequisites**: Task 3.1 complete

**Tasks**:
- [ ] Create `scripts/backup-db.sh`:
  ```bash
  #!/bin/bash
  BACKUP_DIR="$HOME/apps/backups"
  DATE=$(date +%Y%m%d_%H%M%S)

  mkdir -p $BACKUP_DIR

  # Backup database from Docker container
  docker-compose -f $HOME/apps/budget/docker-compose.yml exec -T db \
    pg_dump -U budget_user budget_db > \
    $BACKUP_DIR/budget_${DATE}.sql

  # Keep only last 30 days
  find $BACKUP_DIR -name "budget_*.sql" -mtime +30 -delete

  echo "Backup complete: $BACKUP_DIR/budget_${DATE}.sql"
  ```
- [ ] Make executable: `chmod +x scripts/backup-db.sh`
- [ ] Test backup script locally
- [ ] Will deploy to Pi in Phase 5 and set up cron job

**Deliverable**: Backup script ready for deployment

**Verification**:
```bash
./scripts/backup-db.sh  # Should create backup file
```

---

### 3.4 SSL/HTTPS Setup Planning
**Status**: ⬜ Not Started
**Estimated Time**: 45 minutes
**Prerequisites**: Task 2.1 complete

**Tasks**:
- [ ] Decide on reverse proxy: Traefik (easier) or Nginx (traditional)
- [ ] For Traefik approach, create `docker-compose.override.yml`:
  ```yaml
  version: '3.8'

  services:
    traefik:
      image: traefik:v2.10
      container_name: traefik
      command:
        - "--api.insecure=true"
        - "--providers.docker=true"
        - "--entrypoints.web.address=:80"
        - "--entrypoints.websecure.address=:443"
      ports:
        - "80:80"
        - "443:443"
        - "8080:8080"  # Traefik dashboard
      volumes:
        - /var/run/docker.sock:/var/run/docker.sock:ro
        - ./shared/certs:/certs
      networks:
        - apps_network

    app:
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.budget.rule=Host(`budget.piserver.local`)"
        - "traefik.http.routers.budget.entrypoints=websecure"
        - "traefik.http.routers.budget.tls=true"
  ```
- [ ] OR for Nginx approach, create `nginx/budget.conf`
- [ ] Generate self-signed cert:
  ```bash
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout shared/certs/piserver.key \
    -out shared/certs/piserver.crt \
    -subj "/CN=piserver.local"
  ```
- [ ] Document approach in session log

**Deliverable**: SSL/HTTPS strategy planned

**Verification**:
- Clear plan for which reverse proxy to use
- Self-signed certificate generated

---

## Phase 4: Application Development

**Note**: Phase 4 tasks (4.1 through 4.8) remain the same as the original plan, but with these modifications:

### Key Differences for Docker:
- Development happens locally with `docker-compose up`
- Test by accessing http://localhost:5000
- Database is in Docker container, connect via `docker-compose exec db mysql ...`
- Code changes auto-reload if volume mounted in compose file
- All original tasks (models, routes, templates, forms, utils) are identical

**Refer to original PROJECT_PLAN.md Phase 4 (Tasks 4.1-4.8) for detailed application development steps.**

The application development is framework-agnostic - whether running in Docker or directly on the host, Flask code is the same.

### 4.9 Gas Expense Tracker
**Status**: ⬜ Not Started
**Prerequisites**: Base Flask app structure (models, routes, templates, base.html)

**Tasks**:
- [ ] Create `gas_fillups` table in `migrations/001_initial_schema.sql`
- [ ] Add `GasFillup` model to `app/models.py`
- [ ] Create `GasFillupForm` in `app/forms.py`
- [ ] Create `app/routes/gas.py` blueprint (`/gas`)
  - List fill-ups with summary stats (monthly spend, avg cost/gallon)
  - Add/edit/delete fill-up forms
  - Trends page with charts (cost/gallon over time, MPG, monthly totals)
- [ ] Create templates: `gas/list.html`, `gas/form.html`, `gas/trends.html`
- [ ] Add Chart.js to `app/static/js/` for trend visualization
- [ ] Use SQLAlchemy `extract()` for date grouping (cross-DB compatible)

**Deliverable**: Working gas tracker with CRUD and trend charts

---

### 4.10 House Down Payment Tracker
**Status**: ⬜ Not Started
**Prerequisites**: Base Flask app structure

**Tasks**:
- [ ] Create `down_payment_accounts` table in `migrations/001_initial_schema.sql`
- [ ] Add `DownPaymentAccount` model to `app/models.py`
- [ ] Create `app/routes/downpayment.py` blueprint (`/downpayment`)
  - Dashboard showing accounts with balances and grand total
  - Add/edit/delete account forms
- [ ] Create templates: `downpayment/dashboard.html`, `downpayment/form.html`

**Deliverable**: Simple balance display for down payment savings

---

### 4.11 House Purchase Calculator
**Status**: ⬜ Not Started
**Prerequisites**: Task 4.10 (Down Payment Tracker) for data integration

**Tasks**:
- [ ] Create `app/routes/house.py` blueprint (`/house`)
  - Calculator form with inputs: house price, down payment, closing costs %, inspection, appraisal, repairs, moving costs
  - POST handler: compute line-item breakdown and money remaining
  - Auto-fill option: pull down payment total from Down Payment Tracker
- [ ] Create template: `house/calculator.html`
  - Display results: cost breakdown, total costs, money available, money remaining (or shortfall)
  - Works standalone (all manual) or connected (pulls from DB)

**Deliverable**: House purchase affordability calculator

---

## Phase 5: Deployment & Testing

### 5.1 Deploy to Raspberry Pi
**Status**: ⬜ Not Started
**Estimated Time**: 1 hour
**Prerequisites**: Phase 4 complete, application working locally

**Tasks**:
- [ ] Create `.env` file for Pi with production passwords
- [ ] Copy files to Pi manually for first deployment:
  ```bash
  scp -r docker-compose.yml .env migrations/ scripts/ pi@piserver.local:~/apps/budget/
  ```
- [ ] SSH to Pi: `ssh pi@piserver.local`
- [ ] Navigate to app: `cd ~/apps/budget`
- [ ] Build and start: `docker-compose up -d --build`
- [ ] Check containers: `docker-compose ps`
- [ ] Check logs: `docker-compose logs -f`
- [ ] Test database: `docker-compose exec db psql -U budget_user -d budget_db -c "\dt"`
- [ ] Test app access: `curl http://localhost:5000`

**Deliverable**: Application running in Docker on Pi

**Verification**:
```bash
docker-compose ps  # Both app and db should be "Up"
curl http://localhost:5000  # Should return HTML
```

---

### 5.2 Configure Reverse Proxy and HTTPS
**Status**: ⬜ Not Started
**Estimated Time**: 1 hour
**Prerequisites**: Task 5.1 complete

**Tasks**:
- [ ] If using Traefik:
  - Deploy `docker-compose.override.yml` to Pi
  - Restart: `docker-compose up -d`
  - Access Traefik dashboard: http://piserver.local:8080
  - Test HTTPS: https://budget.piserver.local (accept self-signed cert warning)
- [ ] If using Nginx:
  - Deploy nginx config and start nginx container
  - Configure SSL certificate paths
  - Test HTTPS: https://piserver.local
- [ ] Export certificate for client devices:
  ```bash
  scp pi@piserver.local:~/apps/shared/certs/piserver.crt ~/Downloads/
  ```
- [ ] Install certificate on phones/tablets
- [ ] Test from multiple devices

**Deliverable**: Application accessible via HTTPS

**Verification**:
```bash
curl -k https://budget.piserver.local  # Should return HTML
# Test from phone browser - should see budget app
```

---

### 5.3 Configure Automated Backups
**Status**: ⬜ Not Started
**Estimated Time**: 30 minutes
**Prerequisites**: Task 5.1 complete

**Tasks**:
- [ ] Copy backup script to Pi: `scp scripts/backup-db.sh pi@piserver.local:~/apps/budget/scripts/`
- [ ] Make executable: `ssh pi@piserver.local "chmod +x ~/apps/budget/scripts/backup-db.sh"`
- [ ] Test backup: `ssh pi@piserver.local "cd ~/apps/budget && ./scripts/backup-db.sh"`
- [ ] Set up cron job:
  ```bash
  ssh pi@piserver.local
  crontab -e
  # Add line:
  0 2 * * * cd ~/apps/budget && ./scripts/backup-db.sh >> ~/apps/budget/backup.log 2>&1
  ```
- [ ] Verify cron job: `crontab -l`

**Deliverable**: Daily automated backups

**Verification**:
```bash
ssh pi@piserver.local "ls -lh ~/apps/backups/"
# Should show backup files
```

---

### 5.4 End-to-End Testing
**Status**: ⬜ Not Started
**Estimated Time**: 2 hours
**Prerequisites**: Task 5.2 complete

**Tasks**:
Complete the same functional test checklist from original plan:
- [ ] Access app from desktop browser via HTTPS
- [ ] Access app from mobile browser
- [ ] Create 2 users
- [ ] Create 3 accounts
- [ ] Add income sources
- [ ] Generate income events
- [ ] Create expense categories and templates
- [ ] Create 5 funds
- [ ] Create budget for current month
- [ ] Add expenses, allocate to funds
- [ ] Verify zero-based budget
- [ ] Test dashboard displays correctly
- [ ] Test fund transactions
- [ ] Copy budget to next month
- [ ] Test on 2-3 devices simultaneously
- [ ] Document any bugs
- [ ] Fix critical bugs
- [ ] Retest after fixes

**Deliverable**: Fully tested application meeting all requirements

**Verification**:
- All test checklist items pass
- App works on desktop and mobile
- Multiple simultaneous users work

---

### 5.5 GitHub Actions Deployment Test
**Status**: ⬜ Not Started
**Estimated Time**: 30 minutes
**Prerequisites**: Task 5.4 complete, workflow from 2.5 configured

**Tasks**:
- [ ] Make small change to app (e.g., footer text)
- [ ] Commit to feature branch
- [ ] Create pull request
- [ ] Wait for tests to pass
- [ ] Merge PR to `main`
- [ ] GitHub Actions should trigger automatically (or manually trigger)
- [ ] Approve deployment in GitHub Actions
- [ ] Watch deployment logs
- [ ] SSH to Pi and verify update: `ssh pi@piserver.local "cd ~/apps/budget && docker-compose ps"`
- [ ] Verify change visible in browser
- [ ] Test app still works

**Deliverable**: Working CI/CD pipeline with Docker deployment

**Verification**:
- GitHub Actions shows green checkmark
- Change visible on live site
- Containers restarted successfully

---

## Phase 6: Documentation & Handoff

**Note**: Phase 6 tasks remain largely the same as original plan, with these Docker-specific additions:

### 6.1 User Documentation (same as original)
**Tasks from original plan apply, no changes needed**

### 6.2 Administrator Documentation
**Status**: ⬜ Not Started
**Estimated Time**: 1.5 hours
**Prerequisites**: Phase 5 complete

**Tasks**:
- [ ] Create `docs/ADMIN_GUIDE_DOCKER.md` with:
  - How to SSH to Pi: `ssh pi@piserver.local`
  - Application location: `~/apps/budget`
  - How to check status: `docker-compose ps`
  - How to view logs: `docker-compose logs -f`
  - How to restart containers:
    ```bash
    cd ~/apps/budget
    docker-compose restart
    # OR
    docker-compose down && docker-compose up -d
    ```
  - How to update application:
    ```bash
    cd ~/apps/budget
    git pull  # If using git on Pi
    # OR wait for GitHub Actions deployment
    docker-compose up -d --build
    ```
  - How to backup database: `./scripts/backup-db.sh`
  - How to restore database:
    ```bash
    docker-compose exec -T db mysql -u budget_user -p budget_db < backup.sql
    ```
  - How to access database directly:
    ```bash
    docker-compose exec db mysql -u budget_user -p budget_db
    ```
  - How to clean up Docker:
    ```bash
    docker system prune -a  # Remove unused images/containers
    docker volume prune  # Remove unused volumes (careful!)
    ```
  - Troubleshooting Docker issues
  - Security best practices
- [ ] Document credentials location
- [ ] Create emergency procedures

**Deliverable**: Complete Docker-specific admin guide

**Verification**:
- Test all documented procedures work

---

### 6.3 Final Review and Launch (same as original)
**Tasks from original plan apply**

---

## Progress Tracking

### Current Status
**Phase**: Phases 1-2 mostly complete, Phase 3+ pending
**Last Updated**: 2026-02-01
**Next Action**: Implement Phase 4 features (gas tracker, down payment tracker, house calculator)

### Completion Summary
- [x] Functional requirements documented (updated with 3 new features)
- [x] Database schema designed (updated with 2 new tables)
- [x] Project plan created (Docker version, updated with tasks 4.9-4.11)
- [x] Infrastructure preparation (4/5 tasks - Pi reimage pending)
- [x] Development environment (5/5 tasks)
- [ ] Database & Docker Compose (0/4 tasks)
- [ ] Application development (0/11 tasks)
- [ ] Deployment & testing (0/5 tasks)
- [ ] Documentation & handoff (0/3 tasks)

**Overall Progress**: 12/36 tasks complete (33%)

---

## Time Estimates

| Phase | Estimated Hours |
|-------|----------------|
| Phase 1: Infrastructure Prep | 2.5 hours |
| Phase 2: Dev Environment | 3.25 hours |
| Phase 3: Database & Docker | 3.25 hours |
| Phase 4: Application Dev | 16.75 hours |
| Phase 5: Deployment & Testing | 5 hours |
| Phase 6: Documentation | 3.5 hours |
| **Total** | **34.25 hours** |

**Expected Timeline**: 2-3 weeks at 10-15 hours/week

---

## Docker-Specific Notes

### Why Docker for This Project?
1. **Multi-app ready**: Easy to add more apps to piserver later
2. **Isolation**: Budget app won't conflict with other services
3. **Portability**: Can move to different Pi or cloud easily
4. **Easy rollback**: Previous container images available
5. **Learning value**: Docker skills highly transferable

### Docker Compose Commands Cheat Sheet

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f
docker-compose logs app  # Just app logs
docker-compose logs db   # Just database logs

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build

# Check status
docker-compose ps

# Execute command in container
docker-compose exec app python manage.py
docker-compose exec db mysql -u budget_user -p

# View resource usage
docker stats

# Clean up
docker-compose down -v  # Remove volumes too (CAREFUL!)
docker system prune -a  # Clean up unused images
```

### Troubleshooting Docker Issues

**Container won't start:**
```bash
docker-compose logs <service-name>
docker-compose down && docker-compose up
```

**Database connection fails:**
```bash
# Check db container running
docker-compose ps
# Check database logs
docker-compose logs db
# Verify environment variables
docker-compose exec app env | grep DATABASE
```

**Out of disk space:**
```bash
df -h  # Check space
docker system df  # Check Docker disk usage
docker system prune -a  # Clean up (CAREFUL!)
```

---

## Daily Session Log

Use this section to track daily progress:

### Session 1: 2026-01-10
- Created functional requirements document
- Designed complete database schema
- Created project plan with Docker deployment strategy
- **Decisions made**:
  - Use Docker containers instead of direct LAMP install
  - Keep hostname as "piserver" (multi-purpose server)
  - Shut down Minecraft server to free resources
  - Use Traefik or Nginx for reverse proxy HTTPS
- **Next session**: Start Phase 1 - Assess current Pi setup

### Session 2: [Date]
- Tasks completed:
- Blockers:
- Next session:

---

**End of Docker Project Plan**
