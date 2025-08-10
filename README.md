# RVM Ecosystem Backend

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

## Data Model Overview

This section provides a visual representation and explanation of the core database schema, outlining the relationships between different entities in the RVM Ecosystem Backend.

### Entity-Relationship Diagram (ERD)

![RVM Ecosystem ER Diagram](rvm-ecosystem-ERD.svg)

*A visual representation of the database schema for the RVM Ecosystem Backend.*

### Schema Explanation and Relationships

The RVM Ecosystem is built around several interconnected models designed for scalability and clear data representation:

*   **`User` and `UserRole`**: 
    *   **Relationship:** One-to-Many (`UserRole` to `User`). A `UserRole` (e.g., "Regular User", "Admin", "Technician") can be assigned to multiple `Users`. Each `User` has one `UserRole`.
    *   **Purpose:** Manages user authentication, personal details, and role-based access within the system.

*   **`MaterialType`**:
    *   **Purpose:** Defines different recyclable materials (e.g., Plastic, Glass, Metal) and their corresponding point values per kilogram (`points_per_kg`). This allows for flexible and configurable reward calculations.

*   **`RVM` (Recycling Vending Machine)**:
    *   **Purpose:** Represents the physical recycling machines, storing their location, operational status, and the timestamp of their `last_usage`.

*   **`RewardWallet`**:
    *   **Relationship:** One-to-One (`User` to `RewardWallet`). Each `User` has exactly one `RewardWallet` that acts as their central balance. This is enforced by `RewardWallet` using `user_id` as its primary key and a one-to-one foreign key to `User`.
    *   **Purpose:** Stores a user's current accumulated `points` and `credit`.

*   **`RewardTransaction`**:
    *   **Relationship:** One-to-Many (`RewardWallet` to `RewardTransaction`). Each `RewardWallet` can have multiple `RewardTransaction` records.
    *   **Purpose:** Provides a complete audit trail of all changes to a user's `RewardWallet` balance, including the `change_amount` and `reason` for the transaction.

*   **`RecyclingActivity`**:
    *   **Relationship:** Many-to-One with `User`, `RVM`, and `MaterialType`. Each activity is linked to one user, one RVM, and one material type.
    *   **Purpose:** Records individual recycling events, including the `weight` of material deposited and the `points_earned` from that specific activity. The `timestamp` captures when the activity occurred. This model's `save` method also updates the associated RVM's `last_usage` and adds points to the user's `RewardWallet`.

This structured data model ensures data integrity, facilitates efficient querying, and supports the core functionalities of the RVM ecosystem.

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

You can manually build and run the Docker container:

### 1. Build the Docker Image
```bash
docker build -f Dockerfile -t rvm-backend .
```

### 2. Run the Docker Container
```bash
docker run -p 8000:8000 --name rvm-backend-app rvm-backend
```

**Note:** The container runs in the foreground (not detached) so you can see the logs directly in your terminal.

### 3. Access the Application

Once the container is running:
*   **Web UI (Login/Signup):** `http://localhost:8000/`
*   **API Root (Browsable API):** `http://localhost:8000/api/`
*   **Admin Panel:** `http://localhost:8000/admin/`

### 4. Setup Initial Data (Optional)
In a new terminal, run:
```bash
docker exec -it rvm-backend-app python manage.py setup_initial_data
```

### 5. Container Management
- **View logs:** Logs are displayed directly in the terminal where you ran the container
- **Stop the container:** Press `Ctrl+C` in the terminal where the container is running
- **Remove container:** `docker rm rvm-backend-app`

## Development vs Production

### Development (Current Setup)
- Uses SQLite database (no external dependencies)
- DEBUG mode enabled
- Simple Docker setup with no environment variables needed

### Production (Advanced Setup)
For production deployment, you may want to:
- Use PostgreSQL with `DATABASE_URL` environment variable
- Set `DEBUG=False`
- Configure custom `SECRET_KEY`
- Add proper logging and monitoring

Example production run:
```bash
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e DEBUG="False" \
  -e SECRET_KEY="your_django_secret_key_here" \
  --name rvm-backend-app \
  rvm-backend
```

---

**Built with Django & Django REST Framework** 