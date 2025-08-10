# RVM Ecosystem Backend - Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose

### 1. Clone the Repository
```bash
git clone https://github.com/omarmasoud/rvm-ecosystem-backend.git
cd rvm-ecosystem-backend
```

### 2. Run with Docker Compose (Development)
```bash
# Start the application
docker-compose up --build

# Access the API
# http://localhost:8000
# Admin: http://localhost:8000/admin
# API Docs: http://localhost:8000/docs
```

### 3. Production Deployment

#### Option A: Docker Compose (Production)
```bash
# Build and run production version
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

#### Option B: Docker Only
```bash
# Build the image
docker build -f Dockerfile.prod -t rvm-backend .

# Run with PostgreSQL
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  rvm-backend
```

#### Option C: Docker Compose with Custom Database
```bash
# Set environment variables
export DATABASE_URL=postgresql://user:pass@host:5432/rvm_db
export DEBUG=False
export SECRET_KEY=your-secret-key

# Run
docker-compose up --build
```

## Environment Variables

### Required
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Django secret key

### Optional
- `DEBUG`: Set to False for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Database Setup

### PostgreSQL (Recommended)
```bash
# Using Docker Compose (automatic)
docker-compose up

# Manual setup
createdb rvm_db
python manage.py migrate
python manage.py setup_initial_data
```

### SQLite (Development)
```bash
# Default for local development
python manage.py migrate
python manage.py setup_initial_data
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login

### Core Functionality
- `POST /api/deposit/` - Record recycling deposit
- `GET /api/summary/` - User recycling summary
- `GET /api/rvms/` - List RVMs
- `GET /api/materials/` - List materials

### Admin
- `GET /api/admin/users/` - Manage users
- `GET /api/admin/rvms/` - Manage RVMs
- Admin Interface: `/admin/`

## Default Admin Account
- Email: admin@rvm.com
- Password: admin123

## Health Check
```bash
# Check if API is running
curl http://localhost:8000/

# Expected response:
{
  "message": "RVM Ecosystem API",
  "version": "1.0.0",
  "status": "running"
}
```

## Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## Production Considerations

1. **Set DEBUG=False** in production
2. **Use strong SECRET_KEY**
3. **Configure ALLOWED_HOSTS**
4. **Use HTTPS in production**
5. **Set up proper logging**
6. **Configure backup strategy**
7. **Monitor application health**

## Scaling

### Horizontal Scaling
```bash
# Scale web service
docker-compose up --scale web=3
```

### Load Balancer
Use nginx or similar for load balancing multiple instances.

## Monitoring

### Health Checks
```bash
# Add to docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Logs
```bash
# View logs
docker-compose logs -f web

# Export logs
docker-compose logs web > app.log
``` 