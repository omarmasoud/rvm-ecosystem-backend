## RVM Ecosystem Backend

Django REST Framework API for recycling vending machines and user rewards.

## User Manual

This manual provides a guide for interacting with the RVM Ecosystem Backend, covering both the web-based user interface and the API endpoints for general users and administrators.

### 1. General User Guide

#### 1.1. Web UI Access

Access the user-facing web interface for basic operations:

*   **Login Page:** `http://127.0.0.1:8000/`
    *   Use this page to log in with your existing credentials.
*   **Sign Up Page:** `http://127.0.0.1:8000/signup/`
    *   If you don't have an account, click the "Sign Up" link on the login page or navigate directly here to register.
    *   After successful signup, you will be redirected to a confirmation page.
*   **Signup Success Page:** `http://127.0.0.1:8000/success/`
    *   Confirms your registration and provides information about the system.

#### 1.2. Core API Functionality (For Developers/Integrators)

All API endpoints are accessible under the `/api/` prefix. Authentication is required for most endpoints except registration and initial login.

**Authentication:**
*   **Register New User:** `POST /api/auth/register/`
    *   **Purpose:** Create a new user account.
    *   **Required Fields:** `email`, `first_name`, `last_name`, `password`, `password_confirm`, (optional: `phone`)
*   **Login & Get Token:** `POST /api/auth/login/`
    *   **Purpose:** Authenticate user and receive an API token for subsequent authenticated requests.
    *   **Required Fields:** `email`, `password`

**Authenticated User Endpoints:**
(Requires `Authorization: Token YOUR_AUTH_TOKEN` header)

*   **Log Recyclable Deposit:** `POST /api/deposit/`
    *   **Purpose:** Record a recycling transaction at an RVM.
    *   **Required Fields:** `rvm` (RVM ID), `material` (MaterialType ID), `weight` (in kg)
    *   **Note:** Automatically calculates and awards points. This endpoint only accepts `POST` requests.
*   **Get User Summary:** `GET /api/summary/`
    *   **Purpose:** Retrieve your total recycled weight, points earned, deposit count, membership date, and current wallet balance.
*   **View Reward Wallet:** `GET /api/wallet/`
    *   **Purpose:** See your current points and credit balance, including recent transactions.
*   **View/Update User Profile:** `GET, PUT, PATCH /api/profile/`
    *   **Purpose:** Retrieve or update your own user profile information.
*   **List Material Types:** `GET /api/materials/`
    *   **Purpose:** View available recyclable materials and their point values. (Read-only)
*   **List RVMs (Discovery API):** `GET /api/rvms/`
    *   **Purpose:** Find active RVMs. Supports advanced filtering.
    *   **Filters:**
        *   `id`: Exact RVM ID (e.g., `?id=123`) - must be 0 or greater.
        *   `name`: Partial, case-insensitive match for RVM name (e.g., `?name=main mall`).
        *   `status`: Exact match for RVM status (Dropdown: `active`, `inactive`, `maintenance`).
        *   `location`: Partial, case-insensitive match for RVM location (e.g., `?location=zama`).
*   **View Your Recycling Activities:** `GET /api/activities/`
    *   **Purpose:** List your personal recycling transaction history.

#### 1.3. Browsable API (Interactive Interface)

An interactive web interface for exploring and testing all API endpoints is available:

*   **Access Point:** `http://127.0.0.1:8000/api/`
*   **Usage:**
    1.  Navigate to the **Access Point** URL.
    2.  You will see a list of top-level API resources.
    3.  **Click on any resource link** (e.g., `/materials/`, `/rvms/`, `/deposit/`) to go to its dedicated page.
    4.  On the resource's page, you will find:
        *   `GET` results for listing resources.
        *   Interactive **forms for `POST`, `PUT`, `PATCH`, and `DELETE`** requests (if supported by the endpoint and your authentication).
        *   Filter fields for `GET` requests (e.g., on `/api/rvms/`).
    5.  To interact with authenticated endpoints, ensure you are logged in (via the main web UI or the `/api/auth/login/` API) as the Browsable API uses session authentication once you're logged in.

### 2. Administrator Guide

Administrators have full control over the system's data via the Django Admin panel and dedicated Admin API Endpoints.

#### 2.1. Django Admin Panel

*   **URL:** `http://127.0.0.1:8000/admin/`
*   **Default Credentials:**
    *   Email: `admin@rvm.com`
    *   Password: `admin123` (or your configured admin credentials)
*   **Functionality:** Use this traditional Django interface for easy management of all models (Users, RVMs, Material Types, Recycling Activities, Reward Wallets, etc.). Provides a comprehensive overview and management tools.

#### 2.2. Admin API Endpoints (For Developers/Advanced Integrators)

These endpoints provide full CRUD operations for all system models. They are accessible under the `/api/admin/` prefix and **require administrator privileges**.

*   **Login as Admin:** Ensure you are logged into the Django Admin panel or have an admin user's authentication token.
*   **Usage via Browsable API:** Similar to general user API usage, navigate to the specific admin endpoint.
    *   **Admin Users:** `GET, POST, PUT, PATCH, DELETE /api/admin/users/`
    *   **Admin RVMs:** `GET, POST, PUT, PATCH, DELETE /api/admin/rvms/`
    *   **Admin Recycling Activities:** `GET, POST, PUT, PATCH, DELETE /api/admin/activities/`
        *   Supports additional filters: `user` (User ID), `rvm` (RVM ID), `start_date`, `end_date`.
    *   **Admin Material Types:** `GET, POST, PUT, PATCH, DELETE /api/admin/materials/`
    *   **Admin Reward Wallets:** `GET, POST, PUT, PATCH, DELETE /api/admin/wallets/`

## Features

### Data Modeling & Core Functionality

*   **User Management:** Custom user model with email-based authentication, user roles, and a `summary()` method for recycling statistics.
*   **RVM Management:** Model for Recycling Vending Machines, including location, status (active, inactive, maintenance), and last usage tracking.
*   **Recycling Activity:** Detailed logging of each recycling transaction, linked to users and RVMs.
*   **Reward System:** User reward wallets with points and credit balances, complete with an audit trail of transactions.
*   **Material Types:** Configurable recyclable material types with associated point values.

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

### Admin Access (Default Credentials)
- URL: `http://127.0.0.1:8000/admin/`
- Email: `admin@rvm.com`
- Password: `admin123`

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

Built with Django & Django REST Framework 