# DISCO Complaints Management System

A Django-based web application for managing customer complaints with structured escalation workflows, email notifications, and leadership dashboards.

## Features
- Customer complaint submission with unique ticket IDs
- Automatic staff assignment by complaint category
- Escalation workflow between staff levels
- Email notifications (acknowledgement, escalation, resolution)
- Customer satisfaction feedback
- Leadership dashboard with complaint metrics
- Role-based access (staff, leadership)

## Tech Stack
- Python / Django
- PostgreSQL
- Bootstrap 5
- Gunicorn + Nginx
- Google SMTP

## Core URLs
- Submit complaint: `/complaints/new/`
- Staff login: `/accounts/login/`
- Staff tickets: `/staff/tickets/`
- Leadership dashboard: `/staff/dashboard/`

## Setup (Local)
```bash
git clone https://github.com/YOUR_USERNAME/disco-complaints-portal.git
cd disco-complaints-portal
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

Author
Lucky Ejakpovi