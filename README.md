## RVM Ecosystem Backend

Django REST Framework API for recycling vending machines and user rewards.

## Features

### Data Modeling & Core Functionality

*   **User Management:** Custom user model with email-based authentication, user roles, and a `summary()` method for recycling statistics.
*   **RVM Management:** Model for Recycling Vending Machines, including location, status (active, inactive, maintenance), and last usage tracking.
*   **Recycling Activity:** Detailed logging of each recycling transaction, linked to users and RVMs.
*   **Reward System:** User reward wallets with points and credit balances, complete with an audit trail of transactions.
*   **Material Types:** Configurable recyclable material types with associated point values.

### API Endpoints

All API endpoints are accessible under the `/api/` prefix.

#### Authentication
*   `POST /api/auth/register/` - User registration
*   `POST /api/auth/login/` - User login (returns authentication token)

#### Core Functionality
*   `POST /api/deposit/` - Record recycling deposit (auto-calculates points)
*   `GET /api/summary/` - User recycling summary & current wallet balance
*   `GET /api/rvms/` - List RVMs with advanced filtering (ID, Name, Status (dropdown), Location)
*   `GET /api/materials/` - List available materials

#### Admin Endpoints
*   Full CRUD (Create, Retrieve, Update, Delete) operations for all models, accessible via `/api/admin/`.

#### Browsable API
*   An interactive, automatically generated web UI for all API endpoints, including filtering forms, is available at `/api/`.

### Web UI Endpoints (Template-based)

These endpoints provide basic template-based user interaction outside the API.

*   `/` - Custom Login Page
*   `/signup/` - User Registration (Sign Up) Page
*   `/success/` - Signup Success Confirmation Page

## Setup

### Requirements
- Python 3.8+
- Django 5.1+
- Django REST Framework
- Django Filter

### Installation
```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py setup_initial_data # If applicable, for initial data
python manage.py runserver
```

### Admin Access
- URL: `http://127.0.0.1:8000/admin/`
- Email: `admin@rvm.com`
- Password: `admin123` (or your configured admin credentials)

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start with Docker
```bash
# Clone the repository
git clone https://github.com/omarmasoud/rvm-ecosystem-backend.git
cd rvm-ecosystem-backend

# Run with Docker Compose (migrations run automatically)
docker-compose up --build

# Access the application
# Web UI: http://localhost:8000
# API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/docs/
```

### Production Deployment
```bash
# Build production image (migrations run automatically)
docker build -f Dockerfile.prod -t rvm-backend .

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e DEBUG=False \
  rvm-backend
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Set to `False` for production
- `SECRET_KEY`: Django secret key

## Egyptian Context

- RVM locations in Cairo (Maadi, Zamalek, Heliopolis, etc.)
- Egyptian admin user (Ahmed Mahmoud)
- Realistic Cairo addresses

## Task Requirements Met

- Models for Users, RVMs, Recycling Activity, Reward Wallet
- User.summary() method returning key stats
- Scalable design with proper relationships
- Clean admin interface for management
- Comprehensive API endpoints for all core functionality

Built with Django & Django REST Framework 