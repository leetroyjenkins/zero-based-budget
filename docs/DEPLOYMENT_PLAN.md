# Personal Budget App - Raspberry Pi Deployment Plan

## Executive Summary
This plan outlines the step-by-step process to migrate the Personal Budget Manager from a Streamlit application to a Flask-based LAMP stack deployment on a Raspberry Pi 4/5. The deployment will provide secure, multi-user access on the local network with HTTPS encryption.

**Estimated Effort**: 15-25 hours across 2-3 weeks
**Skill Level**: Beginner-Intermediate (learning opportunity)
**Risk Level**: Low-Medium

---

## Phase 1: Environment Preparation

### Step 1: Raspberry Pi Setup
**Goal**: Prepare the Raspberry Pi with updated OS and basic configuration

**Tasks**:
1. Install latest Raspberry Pi OS (64-bit recommended for Pi 4/5)
   - Download from raspberrypi.com/software
   - Flash to microSD card using Raspberry Pi Imager
   - Enable SSH during setup for remote access

2. Initial Pi configuration
   ```bash
   sudo raspi-config
   ```
   - Set hostname (e.g., "budgetpi")
   - Configure WiFi/Ethernet
   - Set timezone
   - Expand filesystem
   - Set strong password

3. Update system packages
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

4. Configure static IP address (recommended)
   - Edit `/etc/dhcpcd.conf` or use router DHCP reservation
   - Document IP address for access (e.g., 192.168.1.100)

5. Install basic utilities
   ```bash
   sudo apt install -y git vim curl wget htop
   ```

**Deliverable**: Raspberry Pi running latest OS with static IP and SSH access
**Estimated Time**: 1-2 hours

---

### Step 2: LAMP Stack Installation
**Goal**: Install and configure Apache, MariaDB, and Python environment

**Tasks**:

1. Install Apache web server
   ```bash
   sudo apt install -y apache2
   sudo systemctl enable apache2
   sudo systemctl start apache2
   ```
   - Verify at http://raspberrypi.local or http://[PI_IP]

2. Install MariaDB server
   ```bash
   sudo apt install -y mariadb-server mariadb-client
   sudo systemctl enable mariadb
   sudo systemctl start mariadb
   ```

3. Secure MariaDB installation
   ```bash
   sudo mysql_secure_installation
   ```
   - Set root password
   - Remove anonymous users
   - Disallow root login remotely
   - Remove test database
   - Reload privileges

4. Install Python and mod_wsgi
   ```bash
   sudo apt install -y python3 python3-pip python3-venv
   sudo apt install -y libapache2-mod-wsgi-py3
   ```

5. Enable Apache modules
   ```bash
   sudo a2enmod wsgi
   sudo a2enmod ssl
   sudo a2enmod rewrite
   sudo systemctl restart apache2
   ```

6. Optional: Install phpMyAdmin for database management
   ```bash
   sudo apt install -y phpmyadmin
   ```
   - Select Apache2 as web server
   - Configure database for phpMyAdmin

**Deliverable**: Fully functional LAMP stack with all services running
**Estimated Time**: 2-3 hours

---

## Phase 2: Database Setup

### Step 3: Create Database and User
**Goal**: Set up MariaDB database for the budget application

**Tasks**:

1. Create database and user
   ```bash
   sudo mysql -u root -p
   ```
   ```sql
   CREATE DATABASE budget_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'budget_user'@'localhost' IDENTIFIED BY 'secure_password_here';
   GRANT ALL PRIVILEGES ON budget_db.* TO 'budget_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

2. Test database connection
   ```bash
   mysql -u budget_user -p budget_db
   ```

3. Document database credentials securely
   - Store in password manager
   - Will be used in application config

**Deliverable**: Empty budget_db database ready for schema creation
**Estimated Time**: 30 minutes

---

### Step 4: Database Schema Migration
**Goal**: Recreate SQLite schema in MariaDB and prepare migration scripts

**Tasks**:

1. Analyze existing SQLite schema
   ```bash
   sqlite3 budget.db .schema > schema.sql
   ```

2. Create MySQL-compatible schema file
   - Convert SQLite syntax to MySQL
   - Adjust data types (TEXT → VARCHAR, INTEGER → INT, etc.)
   - Add proper indexes and foreign keys

3. Create `schema_mysql.sql` with all tables:
   - users
   - income_sources
   - paycheck_deductions
   - pay_periods
   - expense_categories
   - monthly_expenses
   - savings_goals
   - budget_periods

4. Apply schema to MariaDB
   ```bash
   mysql -u budget_user -p budget_db < schema_mysql.sql
   ```

5. Create Python migration script `migrate_data.py`
   - Read from SQLite
   - Write to MariaDB
   - Verify record counts match

6. Test migration with copy of production data
   ```bash
   python migrate_data.py --source budget.db --test
   ```

**Deliverable**: MariaDB schema matching SQLite structure + migration script
**Estimated Time**: 2-3 hours

---

## Phase 3: Flask Application Development

### Step 5: Project Structure Setup
**Goal**: Create Flask application structure

**Tasks**:

1. Create application directory
   ```bash
   sudo mkdir -p /var/www/budget
   sudo chown $USER:www-data /var/www/budget
   cd /var/www/budget
   ```

2. Initialize Git repository
   ```bash
   git init
   git remote add origin [your-repo-url]
   ```

3. Create virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Create project structure
   ```
   /var/www/budget/
   ├── app/
   │   ├── __init__.py
   │   ├── models.py
   │   ├── routes.py
   │   ├── forms.py
   │   ├── utils.py
   │   ├── templates/
   │   │   ├── base.html
   │   │   ├── dashboard.html
   │   │   ├── setup.html
   │   │   ├── income.html
   │   │   ├── expenses.html
   │   │   ├── savings.html
   │   │   └── pay_periods.html
   │   └── static/
   │       ├── css/
   │       ├── js/
   │       └── img/
   ├── migrations/
   ├── tests/
   ├── venv/
   ├── config.py
   ├── wsgi.py
   ├── requirements.txt
   └── .env
   ```

5. Create `requirements.txt`
   ```
   Flask==3.0.0
   Flask-SQLAlchemy==3.1.1
   Flask-Login==0.6.3
   Flask-WTF==1.2.1
   pymysql==1.1.0
   cryptography==41.0.7
   python-dotenv==1.0.0
   pandas==2.2.0
   gunicorn==21.2.0
   ```

6. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

**Deliverable**: Flask project skeleton with proper directory structure
**Estimated Time**: 1 hour

---

### Step 6: Core Application Development
**Goal**: Build Flask application with all budget features

**Tasks**:

1. Create `config.py` for application settings
   - Database connection string
   - Secret key for sessions
   - Debug/production modes

2. Create `.env` for sensitive data
   ```
   DATABASE_URL=mysql+pymysql://budget_user:password@localhost/budget_db
   SECRET_KEY=[generated-secret-key]
   FLASK_ENV=production
   ```

3. Develop `app/models.py` - SQLAlchemy models
   - User model
   - IncomeSource model
   - PaycheckDeduction model
   - PayPeriod model
   - ExpenseCategory model
   - MonthlyExpense model
   - SavingsGoal model
   - BudgetPeriod model

4. Develop `app/routes.py` - Application routes
   - Dashboard view (`/`)
   - Setup page (`/setup`)
   - Income & Deductions (`/income`)
   - Expenses (`/expenses`)
   - Savings Goals (`/savings`)
   - Pay Periods (`/pay-periods`)
   - API endpoints for AJAX operations

5. Develop `app/forms.py` - WTForms for data entry
   - UserForm
   - IncomeSourceForm
   - DeductionForm
   - ExpenseForm
   - SavingsGoalForm

6. Develop `app/utils.py` - Business logic
   - Port `generate_pay_periods()` from init_db.py
   - Port `calculate_net_pay()` from init_db.py
   - Add helper functions

7. Create HTML templates (responsive with Bootstrap)
   - `base.html` - Layout with navigation
   - `dashboard.html` - Overview with charts
   - `setup.html` - User and category setup
   - `income.html` - Income sources and deductions
   - `expenses.html` - Monthly expense budgeting
   - `savings.html` - Savings goals tracking
   - `pay_periods.html` - Pay period generation

8. Add CSS/JS for interactivity
   - Form validation
   - AJAX for dynamic updates
   - Charts for dashboard (Chart.js or similar)
   - Mobile-responsive design

9. Create `app/__init__.py` - Application factory
   ```python
   from flask import Flask
   from flask_sqlalchemy import SQLAlchemy
   from flask_login import LoginManager

   db = SQLAlchemy()
   login_manager = LoginManager()

   def create_app():
       app = Flask(__name__)
       app.config.from_object('config.Config')

       db.init_app(app)
       login_manager.init_app(app)

       from app import routes
       app.register_blueprint(routes.bp)

       return app
   ```

10. Create `wsgi.py` - WSGI entry point
    ```python
    from app import create_app

    application = create_app()

    if __name__ == "__main__":
        application.run()
    ```

**Deliverable**: Fully functional Flask application matching Streamlit features
**Estimated Time**: 10-15 hours (largest phase)

**Milestones**:
- [ ] Database models defined and tested
- [ ] All routes rendering properly
- [ ] Forms handling data input
- [ ] Business logic functions working
- [ ] Templates responsive on mobile
- [ ] Dashboard showing budget data

---

### Step 7: Local Testing
**Goal**: Test application locally before Apache integration

**Tasks**:

1. Run development server
   ```bash
   source venv/bin/activate
   export FLASK_APP=wsgi.py
   flask run --host=0.0.0.0 --port=5000
   ```

2. Access from local network
   - http://[PI_IP]:5000

3. Test all features
   - [ ] Create users and income sources
   - [ ] Add deductions
   - [ ] Generate pay periods
   - [ ] Create monthly budgets
   - [ ] Add savings goals
   - [ ] View dashboard
   - [ ] Test on mobile device

4. Run data migration
   ```bash
   python migrate_data.py --source ../personal-budget/budget.db
   ```

5. Verify migrated data displays correctly

6. Fix bugs and iterate

**Deliverable**: Fully tested Flask application with real data
**Estimated Time**: 2-3 hours

---

## Phase 4: Production Deployment

### Step 8: Apache Configuration
**Goal**: Configure Apache to serve Flask app via mod_wsgi

**Tasks**:

1. Create Apache virtual host config
   ```bash
   sudo vim /etc/apache2/sites-available/budget.conf
   ```

   ```apache
   <VirtualHost *:80>
       ServerName budgetpi.local
       ServerAlias 192.168.1.100

       Redirect permanent / https://budgetpi.local/
   </VirtualHost>

   <VirtualHost *:443>
       ServerName budgetpi.local
       ServerAlias 192.168.1.100

       SSLEngine on
       SSLCertificateFile /etc/ssl/certs/budget-selfsigned.crt
       SSLCertificateKeyFile /etc/ssl/private/budget-selfsigned.key

       WSGIDaemonProcess budget user=www-data group=www-data threads=5 python-home=/var/www/budget/venv
       WSGIScriptAlias / /var/www/budget/wsgi.py

       <Directory /var/www/budget>
           WSGIProcessGroup budget
           WSGIApplicationGroup %{GLOBAL}
           Require all granted
       </Directory>

       Alias /static /var/www/budget/app/static
       <Directory /var/www/budget/app/static>
           Require all granted
       </Directory>

       ErrorLog ${APACHE_LOG_DIR}/budget_error.log
       CustomLog ${APACHE_LOG_DIR}/budget_access.log combined
   </VirtualHost>
   ```

2. Set proper permissions
   ```bash
   sudo chown -R www-data:www-data /var/www/budget
   sudo chmod -R 755 /var/www/budget
   ```

3. Enable site and disable default
   ```bash
   sudo a2ensite budget.conf
   sudo a2dissite 000-default.conf
   sudo systemctl reload apache2
   ```

**Deliverable**: Apache serving Flask app on port 80 (redirecting to 443)
**Estimated Time**: 1 hour

---

### Step 9: SSL/HTTPS Configuration
**Goal**: Enable HTTPS with self-signed certificate

**Tasks**:

1. Generate self-signed SSL certificate
   ```bash
   sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
       -keyout /etc/ssl/private/budget-selfsigned.key \
       -out /etc/ssl/certs/budget-selfsigned.crt
   ```
   - Fill in certificate details (CN=budgetpi.local)

2. Create strong Diffie-Hellman group
   ```bash
   sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
   ```

3. Configure SSL parameters
   ```bash
   sudo vim /etc/apache2/conf-available/ssl-params.conf
   ```
   - Add modern SSL/TLS configuration
   - Disable weak ciphers

4. Enable SSL configuration
   ```bash
   sudo a2enconf ssl-params
   sudo systemctl reload apache2
   ```

5. Test HTTPS access
   - https://budgetpi.local or https://[PI_IP]
   - Accept self-signed certificate warning

6. Document certificate installation for client devices
   - Export certificate
   - Install on phones/tablets to avoid warnings

**Deliverable**: Application accessible via HTTPS with encryption
**Estimated Time**: 1 hour

---

### Step 10: Auto-Start Configuration
**Goal**: Application starts automatically on Pi boot

**Tasks**:

1. Verify services enabled
   ```bash
   sudo systemctl enable apache2
   sudo systemctl enable mariadb
   ```

2. Create health check script
   ```bash
   sudo vim /usr/local/bin/budget-healthcheck.sh
   ```
   ```bash
   #!/bin/bash
   if ! curl -f -k https://localhost > /dev/null 2>&1; then
       systemctl restart apache2
   fi
   ```

3. Make executable
   ```bash
   sudo chmod +x /usr/local/bin/budget-healthcheck.sh
   ```

4. Add to crontab (optional monitoring)
   ```bash
   sudo crontab -e
   ```
   ```
   */5 * * * * /usr/local/bin/budget-healthcheck.sh
   ```

5. Test auto-start
   ```bash
   sudo reboot
   ```
   - Wait for Pi to restart
   - Access application via HTTPS
   - Verify all services running

**Deliverable**: Application automatically available after Pi boot
**Estimated Time**: 30 minutes

---

## Phase 5: Backup and Monitoring

### Step 11: Backup System
**Goal**: Automated database backups

**Tasks**:

1. Create backup script
   ```bash
   sudo vim /usr/local/bin/backup-budget.sh
   ```
   ```bash
   #!/bin/bash
   BACKUP_DIR="/home/pi/backups"
   DATE=$(date +%Y%m%d_%H%M%S)

   mkdir -p $BACKUP_DIR
   mysqldump -u budget_user -p'password' budget_db > $BACKUP_DIR/budget_$DATE.sql

   # Keep only last 30 days
   find $BACKUP_DIR -name "budget_*.sql" -mtime +30 -delete
   ```

2. Make executable
   ```bash
   sudo chmod +x /usr/local/bin/backup-budget.sh
   ```

3. Schedule daily backups
   ```bash
   sudo crontab -e
   ```
   ```
   0 2 * * * /usr/local/bin/backup-budget.sh
   ```

4. Test backup script
   ```bash
   sudo /usr/local/bin/backup-budget.sh
   ```

5. Document restore procedure
   ```bash
   mysql -u budget_user -p budget_db < backup_file.sql
   ```

**Deliverable**: Daily automated database backups
**Estimated Time**: 45 minutes

---

### Step 12: Monitoring and Documentation
**Goal**: Basic monitoring and complete documentation

**Tasks**:

1. Install monitoring tools (optional)
   ```bash
   sudo apt install -y vnstat iftop
   ```

2. Configure Apache log rotation
   - Verify `/etc/logrotate.d/apache2` exists

3. Create user documentation
   - How to access application (URL)
   - How to accept self-signed certificate
   - How to use features
   - Troubleshooting common issues

4. Create admin documentation
   - SSH access details
   - Database credentials (secure)
   - Backup/restore procedures
   - Apache configuration locations
   - How to update application code
   - How to restart services

5. Document IP address and credentials
   - Store securely (password manager)

**Deliverable**: Complete documentation for users and administrators
**Estimated Time**: 1-2 hours

---

## Phase 6: Testing and Validation

### Step 13: System Testing
**Goal**: Comprehensive testing of deployed application

**Test Checklist**:

**Functionality Tests**:
- [ ] All pages load without errors
- [ ] Users can create and manage profiles
- [ ] Income sources can be added/edited/deleted
- [ ] Deductions calculate correctly
- [ ] Pay periods generate accurately
- [ ] Monthly budgets save and display
- [ ] Savings goals track progress
- [ ] Dashboard shows current data

**Multi-User Tests**:
- [ ] 2-3 devices access simultaneously
- [ ] No session conflicts
- [ ] Data updates reflected across sessions

**Performance Tests**:
- [ ] Page load time < 2 seconds
- [ ] Database queries respond quickly
- [ ] No memory leaks over 24 hours

**Security Tests**:
- [ ] HTTPS connection working
- [ ] Self-signed certificate accepted
- [ ] No SQL injection vulnerabilities
- [ ] Session management secure

**Mobile Tests**:
- [ ] Responsive design on phone
- [ ] Touch interactions work
- [ ] Forms usable on mobile
- [ ] Charts/tables readable

**Reliability Tests**:
- [ ] Application survives Pi reboot
- [ ] Services restart automatically
- [ ] Backups running daily
- [ ] Logs rotating properly

**Estimated Time**: 2-3 hours

---

## Rollout Plan

### Go-Live Steps

1. **Final data migration**
   - Run migration script on production SQLite database
   - Verify all records transferred

2. **User notification**
   - Inform household members of new URL
   - Provide certificate installation instructions

3. **Monitor first 48 hours**
   - Check Apache logs for errors
   - Verify backups running
   - Gather user feedback

4. **Iterate and improve**
   - Fix any bugs discovered
   - Optimize performance if needed
   - Add features based on usage

### Rollback Plan

If critical issues arise:
1. Stop Apache: `sudo systemctl stop apache2`
2. Revert to Streamlit on Pi: `streamlit run app.py --server.port 8501`
3. Access via http://[PI_IP]:8501
4. Debug Flask application offline
5. Redeploy when fixed

---

## Future Enhancements (Phase 2)

After successful Phase 1 deployment, consider:

1. **Remote Access**
   - Set up WireGuard VPN server on Pi
   - Configure dynamic DNS
   - Obtain Let's Encrypt certificate
   - Test remote connectivity

2. **Advanced Features**
   - User authentication system
   - Data export/import
   - Budget reports and analytics
   - Email notifications for goals

3. **Performance Optimization**
   - Redis caching layer
   - Database query optimization
   - CDN for static assets

4. **Monitoring**
   - Uptime monitoring
   - Performance metrics
   - Automated alerts

---

## Resource Requirements

### Time Investment
- **Setup & Configuration**: 5-7 hours
- **Application Development**: 10-15 hours
- **Testing & Documentation**: 3-5 hours
- **Total**: 18-27 hours

### Skills Needed
- Basic Linux command line
- Python programming (existing)
- HTML/CSS basics
- SQL fundamentals
- Web server concepts (will learn)

### Learning Resources
- Flask Mega-Tutorial: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- Apache mod_wsgi guide: https://flask.palletsprojects.com/en/latest/deploying/mod_wsgi/
- MariaDB documentation: https://mariadb.org/documentation/
- Bootstrap CSS framework: https://getbootstrap.com/docs/

---

## Success Criteria

**Phase 1 is complete when**:
- ✅ Application accessible at https://budgetpi.local
- ✅ All budget features working
- ✅ 2-3 users can access simultaneously
- ✅ Mobile-responsive interface
- ✅ Auto-starts on Pi boot
- ✅ HTTPS encryption active
- ✅ Daily backups running
- ✅ Documentation complete

---

## Next Steps

**Ready to begin?** Start with Phase 1, Step 1: Raspberry Pi Setup

**Questions before starting?** Review the requirements document or clarify any steps.

**Prefer different approach?** We can also deploy Streamlit behind Apache reverse proxy (faster, keeps existing code).
