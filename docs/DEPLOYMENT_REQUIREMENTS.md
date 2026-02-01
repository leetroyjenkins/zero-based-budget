# Personal Budget App - Raspberry Pi Deployment Requirements

## Project Overview
Deploy the Personal Budget Manager application to a Raspberry Pi 4/5 on the local home network using a LAMP stack architecture, migrating from the current Streamlit implementation to a more robust web application.

## Stakeholder Requirements

### Functional Requirements

#### FR1: Multi-User Access
- Support 2-3 simultaneous users/devices accessing the budget application
- Maintain session management for concurrent household members
- Preserve all existing budget management features:
  - Bi-weekly pay period tracking
  - Paycheck deductions management
  - Monthly expense budgets
  - Savings goals tracking
  - Multi-user financial data

#### FR2: Mobile Accessibility
- Responsive web design that works well on phones and tablets
- Touch-friendly interface for mobile devices
- Maintain full functionality across device sizes

#### FR3: Local Network Access (Phase 1)
- Application accessible via local network IP address
- All household devices can connect when on home WiFi
- No internet dependency for core functionality

#### FR4: Future Remote Access (Phase 2)
- Architecture must support future remote access implementation
- Plan for VPN or secure port forwarding solution
- Consideration for dynamic DNS if needed

### Technical Requirements

#### TR1: LAMP Stack Architecture
- **Linux**: Raspberry Pi OS (Debian-based)
- **Apache**: Apache2 web server with mod_wsgi or mod_php
- **MySQL**: MariaDB database server
- **Python**: Python-based web framework (Flask recommended for this project)

**Rationale**: Full LAMP stack provides learning opportunity and reusable architecture for future projects while maintaining Python expertise.

#### TR2: Database Migration
- Migrate from SQLite to MySQL/MariaDB
- Preserve all existing data schema:
  - users
  - income_sources
  - paycheck_deductions
  - pay_periods
  - expense_categories
  - monthly_expenses
  - savings_goals
  - budget_periods
- Create migration scripts to transfer existing SQLite data to MySQL

#### TR3: Security Requirements
- HTTPS/SSL encryption for all connections
- Self-signed SSL certificate for local network (Phase 1)
- Option to upgrade to Let's Encrypt for remote access (Phase 2)
- Secure user authentication and session management
- Database credentials stored securely (environment variables or config file with proper permissions)

#### TR4: Application Auto-Start
- Application automatically starts on Raspberry Pi boot
- Systemd service configuration for Apache and MariaDB
- Automatic recovery on failure

#### TR5: Hardware Platform
- Raspberry Pi 4 or Pi 5 with 4GB+ RAM
- Sufficient SD card storage (32GB+ recommended)
- Stable power supply
- Wired or WiFi network connection

### Non-Functional Requirements

#### NFR1: Performance
- Page load time under 2 seconds on local network
- Database query optimization for responsive user experience
- Efficient handling of 2-3 concurrent users

#### NFR2: Reliability
- 99% uptime on local network (when Pi is powered)
- Automatic service restart on failure
- Regular automated database backups

#### NFR3: Maintainability
- Clear documentation for configuration and updates
- Modular code structure for easy updates
- Version control integration (Git)

#### NFR4: Usability
- Intuitive web interface matching or improving on Streamlit version
- Consistent UI/UX across devices
- Clear error messages and user feedback

## Technology Stack

### Backend
- **Language**: Python 3.14
- **Framework**: Flask (lightweight, flexible, good learning curve)
- **Database**: MariaDB 10.x
- **ORM**: SQLAlchemy (optional but recommended)
- **Authentication**: Flask-Login or similar

### Frontend
- **Template Engine**: Jinja2 (Flask default)
- **CSS Framework**: Bootstrap 5 or Tailwind CSS (responsive design)
- **JavaScript**: Vanilla JS or Alpine.js for interactivity

### Server Infrastructure
- **Web Server**: Apache 2.4 with mod_wsgi
- **Database Server**: MariaDB
- **Process Management**: systemd
- **SSL/TLS**: OpenSSL (self-signed certificates)

### Development Tools
- **Dependency Management**: uv (existing) or pip with requirements.txt
- **Version Control**: Git
- **Database Management**: phpMyAdmin (optional, for easier DB management)

## Migration Considerations

### From Streamlit to Flask
- Streamlit provides automatic UI generation; Flask requires manual HTML/CSS/JS
- Need to recreate all Streamlit widgets as HTML forms
- Session state management differs significantly
- Budget ~3-4x development time vs. using Streamlit with Apache reverse proxy

### Data Migration
- Export existing SQLite budget.db data
- Import into MariaDB with proper schema recreation
- Verify data integrity post-migration

## Project Phases

### Phase 1: Local Network Deployment (Primary Focus)
- LAMP stack setup on Raspberry Pi
- Application development and migration
- HTTPS with self-signed certificates
- Auto-start configuration
- Testing with household devices

### Phase 2: Remote Access (Future)
- VPN solution (WireGuard or OpenVPN) OR
- Secure port forwarding with Let's Encrypt SSL
- Dynamic DNS configuration if needed
- Enhanced security hardening

## Success Criteria

1. Application accessible via https://raspberrypi.local or https://192.168.x.x from any device on local network
2. All existing budget features functional in new Flask application
3. 2-3 users can access simultaneously without performance degradation
4. Application auto-starts on Pi boot
5. Mobile-responsive interface works on phones and tablets
6. All data successfully migrated from SQLite to MariaDB
7. Secure HTTPS connections established

## Constraints and Risks

### Constraints
- Raspberry Pi limited processing power compared to cloud servers
- Local network only (Phase 1) - no internet access to budget data
- Development time for complete Streamlit-to-Flask migration

### Risks
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Development time longer than expected | High | Start with MVP feature set, iterate |
| Performance issues with MariaDB on Pi | Medium | Optimize queries, consider connection pooling |
| Learning curve for LAMP stack | Medium | Follow tutorials, use proven examples |
| Data migration errors | High | Test migration on copy, verify all data |
| SSL certificate complexity | Low | Use well-documented self-signed cert process |

## Out of Scope (for Phase 1)
- Remote access from outside home network
- Multi-household/tenant architecture
- Advanced analytics or reporting
- Mobile native apps (iOS/Android)
- Automated bill payment integration
- Bank account synchronization

## Dependencies
- Raspberry Pi 4/5 hardware available
- Local network with DHCP or static IP capability
- Router access for port configuration (Phase 2)
- Basic command-line familiarity for Pi setup
