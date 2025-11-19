# Bunyodkor CIMS - Complete Information Management System

A comprehensive management system for Bunyodkor Football Academy built with FastAPI (backend) and React + TypeScript (frontend).

## Features

### Core Functionality
- **Student Management**: Complete student profiles with enrollment tracking
- **Group Management**: Training groups with schedules and capacity management
- **Contract Management**: Student contracts with flexible discount options
- **Payment Processing**:
  - Online payments via Payme and Click
  - Cash payment tracking
  - Parent payment portal
  - Error payment resolution
- **Attendance Tracking**:
  - Session-based attendance marking by teachers
  - Automatic attendance records for all students
  - Attendance history and reports
- **Turnstile Integration**:
  - FaceID-based access control
  - Payment verification before entry
  - Complete entry/exit logging
- **Reports & Analytics**:
  - Dashboard with real-time statistics
  - Revenue reports (daily, monthly, yearly)
  - Debtors list
  - Group statistics
  - Attendance summaries
- **Excel Import**: Bulk student import from Excel files
- **Role-Based Access Control**: Admin, Superuser, Teacher, and Student roles

### User Roles

**Admin**
- Full system access
- Create and manage all users
- Assign permissions to superusers
- View all reports and statistics

**Superuser**
- Configurable permissions
- Manage students, groups, contracts
- Process payments
- Limited administrative access

**Teacher**
- View assigned groups
- Mark attendance for sessions
- View student information
- Track payments and attendance for their groups

**Student**
- View personal information
- Check payment history
- View attendance records
- See upcoming sessions

**Parent (Public)**
- Access payment portal
- Make online payments
- View student information by contract number

## Tech Stack

### Backend
- FastAPI (Python web framework)
- PostgreSQL (Database)
- SQLAlchemy (ORM)
- Pydantic (Data validation)
- JWT (Authentication)
- Alembic (Migrations)

### Frontend
- React 18 + TypeScript
- Vite (Build tool)
- TailwindCSS (Styling)
- React Router (Routing)
- TanStack Query (Data fetching)
- Zustand (State management)
- Axios (HTTP client)

## Project Structure

```
BunyodkorBack/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── init_db.py          # Database initialization
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # Backend documentation
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── store/         # State management
│   │   └── types/         # TypeScript types
│   ├── package.json       # Node dependencies
│   └── README.md          # Frontend documentation
└── README.md              # This file
```

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 12+

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create PostgreSQL database:
```bash
createdb bunyodkor_db
```

4. Configure environment:
```bash
cp .env .env
# Edit .env with your database credentials and settings
```

5. Initialize database:
```bash
python init_db.py
```

6. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000
API documentation at http://localhost:8000/docs

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp .env .env
# Edit .env to set VITE_API_URL if needed
```

3. Run the frontend:
```bash
npm run dev
```

Frontend will be available at http://localhost:3000

### First Time Setup

1. Create admin account:

Visit http://localhost:8000/docs and use the `/api/auth/register/admin` endpoint:

```json
{
  "username": "admin",
  "password": "your-secure-password",
  "email": "admin@bunyodkor.uz",
  "full_name": "System Administrator"
}
```

2. Login with admin credentials at http://localhost:3000/login

3. Start adding students, groups, and contracts!

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register/admin` - Create first admin (one-time)

### Students
- `GET /api/students` - List students
- `POST /api/students` - Create student
- `POST /api/students/import-excel` - Import from Excel

### Payments
- `POST /api/payments/parent/info` - Get payment info (public)
- `GET /api/payments` - List payments
- `GET /api/payments/errors` - List error payments

### Reports
- `GET /api/reports/dashboard` - Dashboard statistics
- `GET /api/reports/debtors` - Debtors list
- `GET /api/reports/revenue/monthly` - Monthly revenue

### Turnstile
- `POST /api/turnstile/verify` - Verify student access

See full API documentation at `/docs` for all endpoints.

## Student Login Credentials

Students are automatically created with login credentials:
- **Username**: `{enrollment_year}{student_id}` (e.g., `202410`)
- **Default Password**: Same as username (e.g., `202410`)

Students should change their password after first login.

## Excel Import Format

For bulk student import, Excel file should have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| first_name | Yes | Student's first name |
| last_name | Yes | Student's last name |
| middle_name | No | Student's middle name |
| date_of_birth | Yes | Birth date (YYYY-MM-DD) |
| parent_phone | Yes | Parent's phone number |
| parent_name | No | Parent's name |
| enrollment_year | Yes | Year of enrollment |
| group_name | No | Group name (must exist) |
| monthly_fee | Yes | Monthly fee amount |
| discount_percentage | No | Discount percentage (0-100) |

## Turnstile Integration

The system supports FaceID turnstile devices. The turnstile should:

1. Recognize student face
2. Send verification request to `/api/turnstile/verify` with:
   - `student_id`
   - `face_match_confidence`
   - `turnstile_id`

3. System will:
   - Verify student exists and is active
   - Check for active contract
   - Verify current month payment
   - Return access decision
   - Log the entry attempt

## Payment Integration

### Payme Integration
- Webhook: `POST /api/payments/payme/webhook`
- Set merchant credentials in `.env`

### Click Integration
- Webhook: `POST /api/payments/click/webhook`
- Set merchant credentials in `.env`

See backend README for detailed payment integration guide.

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Database Migrations
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Production Deployment

### Backend
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend
```bash
npm run build
# Deploy dist/ folder to static hosting
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/bunyodkor_db
SECRET_KEY=your-secret-key
PAYME_MERCHANT_ID=your_merchant_id
PAYME_SECRET_KEY=your_secret_key
CLICK_MERCHANT_ID=your_merchant_id
CLICK_SERVICE_ID=your_service_id
CLICK_SECRET_KEY=your_secret_key
FRONTEND_URL=http://localhost:3000
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Security

- JWT token-based authentication
- Role-based access control
- Password hashing with bcrypt
- SQL injection protection (SQLAlchemy ORM)
- CORS configuration
- Input validation with Pydantic

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Support

For support, contact the development team or create an issue in the repository.

## License

Proprietary - Bunyodkor Football Academy
