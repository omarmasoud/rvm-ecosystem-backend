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


Built with Django & Django REST Framework 