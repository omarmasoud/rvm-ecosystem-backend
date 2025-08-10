# RVM Ecosystem Backend

Django REST Framework API for recycling vending machines and user rewards.

## Task: RVM Ecosystem Data Modeling

Complete backend implementation for Drop Me's recycling ecosystem.

## Setup

### Requirements
- Python 3.8+
- Django 5.1+
- Django REST Framework

### Installation
```bash
pip install djangorestframework coreapi
python manage.py makemigrations
python manage.py migrate
python manage.py setup_initial_data
python manage.py runserver
```

### Admin Access
- URL: http://127.0.0.1:8000/admin/
- Email: admin@rvm.com
- Password: admin123

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start with Docker
```bash
# Clone the repository
git clone https://github.com/omarmasoud/rvm-ecosystem-backend.git
cd rvm-ecosystem-backend

# Run with Docker Compose
docker-compose up --build

# Access the application
# API: http://localhost:8000
# Admin: http://localhost:8000/admin/
# API Docs: http://localhost:8000/docs/
```

### Production Deployment
```bash
# Build production image
docker build -f Dockerfile.prod -t rvm-backend .

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e DEBUG=False \
  rvm-backend
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Set to False for production
- `SECRET_KEY`: Django secret key

## Models

1. User - Custom user model with email authentication
2. UserRole - Role-based access control
3. MaterialType - Recyclable materials with point values
4. RVM - Recycling Vending Machine locations and status
5. RewardWallet - User's current point and credit balance
6. RewardTransaction - Complete audit trail of wallet changes
7. RecyclingActivity - Individual recycling transactions

## API Endpoints

### Authentication
- POST /api/auth/register/ - User registration
- POST /api/auth/login/ - User login

### Core Functionality
- POST /api/deposit/ - Record recycling deposit
- GET /api/summary/ - User recycling summary
- GET /api/rvms/ - List RVMs with filtering
- GET /api/materials/ - List available materials

### Admin Endpoints
- Full CRUD operations for all models

## Database Schema

### User Model
- Email-based authentication
- Phone number and role assignment
- summary() method for recycling stats

### Material Types
- Plastic: 1 point/kg
- Metal: 3 points/kg  
- Glass: 2 points/kg
- Paper: 0.5 points/kg
- Cardboard: 0.75 points/kg

### Reward System
- Auto-calculated points: weight × material.points_per_kg
- Complete transaction history
- Current balance tracking

## Egyptian Context

- RVM locations in Cairo (Maadi, Zamalek, Heliopolis, etc.)
- Egyptian admin user (Ahmed Mahmoud)
- Realistic Cairo addresses

## Task Requirements Met

- Models for Users, RVMs, Recycling Activity, Reward Wallet
- User.summary() method returning key stats
- Scalable design with proper relationships
- Clean admin interface for management
- API endpoints for all core functionality

Built with Django & Django REST Framework 