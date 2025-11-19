# Bunyodkor CIMS Backend

Backend API for Bunyodkor Football Academy Complete Information Management System (CIMS).

## Features

- **User Management**: Admin, Superuser, Teacher, and Student roles
- **Student Management**: Complete student profiles with photo support
- **Group Management**: Training groups with schedules
- **Contract Management**: Student contracts with discounts
- **Payment Processing**: Online (Payme/Click) and cash payments
- **Attendance Tracking**: Session-based attendance with teacher marking
- **Turnstile Integration**: FaceID-based access control with payment verification
- **Reports & Statistics**: Comprehensive analytics and dashboards
- **Excel Import**: Bulk student import functionality

## Tech Stack

- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation
- **JWT**: Authentication
- **Alembic**: Database migrations

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/bunyodkor_db
SECRET_KEY=your-secret-key-here
```

### 3. Create Database

```bash
# Using PostgreSQL
createdb bunyodkor_db

# Or using psql
psql -U postgres
CREATE DATABASE bunyodkor_db;
```

### 4. Initialize Database

```bash
python init_db.py
```

### 5. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## First Time Setup

### Create Admin Account

```bash
curl -X POST "http://localhost:8000/api/auth/register/admin" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-secure-password",
    "email": "admin@bunyodkor.uz",
    "full_name": "System Administrator"
  }'
```

Or use the API documentation at `/docs` to create the admin account.

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register/admin` - Create first admin (one-time)

### Users
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `POST /api/users/{id}/permissions` - Assign permission to superuser

### Students
- `GET /api/students` - List students
- `POST /api/students` - Create student
- `GET /api/students/{id}` - Get student
- `PUT /api/students/{id}` - Update student
- `DELETE /api/students/{id}` - Delete student
- `POST /api/students/import-excel` - Import from Excel

### Groups
- `GET /api/groups` - List groups
- `POST /api/groups` - Create group
- `GET /api/groups/{id}` - Get group
- `PUT /api/groups/{id}` - Update group
- `DELETE /api/groups/{id}` - Delete group

### Contracts
- `GET /api/contracts` - List contracts
- `POST /api/contracts` - Create contract
- `GET /api/contracts/{id}` - Get contract
- `GET /api/contracts/number/{contract_number}` - Get by contract number
- `PUT /api/contracts/{id}` - Update contract
- `DELETE /api/contracts/{id}` - Delete contract

### Payments
- `GET /api/payments` - List payments
- `POST /api/payments` - Create payment
- `GET /api/payments/{id}` - Get payment
- `POST /api/payments/parent/info` - Get payment info for parents
- `POST /api/payments/payme/webhook` - Payme webhook
- `POST /api/payments/click/webhook` - Click webhook
- `GET /api/payments/errors` - List error payments
- `POST /api/payments/errors/{id}/resolve` - Resolve error payment
- `DELETE /api/payments/errors/{id}` - Delete error payment

### Attendance
- `POST /api/attendance/sessions` - Create session
- `GET /api/attendance/sessions` - List sessions
- `GET /api/attendance/sessions/{id}` - Get session
- `PUT /api/attendance/sessions/{id}/complete` - Mark session complete
- `GET /api/attendance` - List attendance records
- `POST /api/attendance` - Create attendance
- `PUT /api/attendance/{id}` - Update attendance
- `GET /api/attendance/student/{id}/history` - Student attendance history

### Turnstile
- `POST /api/turnstile/verify` - Verify student access
- `GET /api/turnstile` - List logs
- `GET /api/turnstile/{id}` - Get log
- `GET /api/turnstile/student/{id}/today` - Check today's access

### Reports
- `GET /api/reports/dashboard` - Dashboard statistics
- `GET /api/reports/revenue/monthly` - Monthly revenue report
- `GET /api/reports/debtors` - Debtors list
- `GET /api/reports/groups/{id}/statistics` - Group statistics
- `GET /api/reports/attendance/summary` - Attendance summary

## Authentication

All endpoints (except login, register-admin, and parent payment info) require authentication.

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your-token>
```

## Roles & Permissions

### Admin
- Full access to all features
- Can create and manage all users
- Can assign permissions to superusers

### Superuser
- Configurable permissions assigned by admin
- Can manage students, groups, contracts, payments
- Cannot manage other users or system settings

### Teacher
- View and manage their own groups
- Mark attendance for their sessions
- View student information in their groups
- View payment status of students in their groups

### Student
- View their own information
- View their payment history
- View their attendance records

## Student Login Credentials

Students are automatically created with login credentials when added to the system:

- **Username**: `{enrollment_year}{student_id}` (e.g., `202410`)
- **Default Password**: Same as username (e.g., `202410`)

Students should change their password after first login.

## Excel Import Format

The Excel file for student import should have the following columns:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| first_name | String | Yes | Student's first name |
| last_name | String | Yes | Student's last name |
| middle_name | String | No | Student's middle name |
| date_of_birth | Date | Yes | Birth date (YYYY-MM-DD) |
| parent_phone | String | Yes | Parent's phone number |
| parent_name | String | No | Parent's name |
| enrollment_year | Integer | Yes | Year of enrollment |
| group_name | String | No | Group name (must exist) |
| monthly_fee | Number | Yes | Monthly fee amount |
| discount_percentage | Number | No | Discount percentage (0-100) |

## Development

### Database Migrations

If you make changes to models, create and run migrations:

```bash
# Initialize alembic (first time only)
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Description"

# Run migrations
alembic upgrade head
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Production Deployment

1. Set strong `SECRET_KEY` in `.env`
2. Use production PostgreSQL database
3. Set `FRONTEND_URL` to your production frontend URL
4. Use a production ASGI server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use Gunicorn with Uvicorn workers:

```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Support

For issues or questions, contact the development team.
