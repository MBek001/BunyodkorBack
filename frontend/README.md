# Bunyodkor CIMS Frontend

Modern React + TypeScript frontend for Bunyodkor Football Academy Complete Information Management System (CIMS).

## Features

- **Role-Based Access Control**: Separate interfaces for Admin, Superuser, Teacher, and Student
- **Admin Dashboard**: Complete system management with statistics and reports
- **Teacher Portal**: Group management and attendance tracking
- **Student Portal**: View personal information, payments, and attendance
- **Parent Payment Portal**: Secure online payment through Payme/Click
- **Excel Import**: Bulk student import functionality
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **React 18**: Modern React with Hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **TanStack Query**: Data fetching and caching
- **Zustand**: State management
- **Axios**: HTTP client
- **date-fns**: Date formatting

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env .env
```

Edit `.env` to set your backend URL:
```
VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at http://localhost:3000

### 4. Build for Production

```bash
npm run build
```

The production build will be in the `dist` folder.

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable components
│   │   ├── common/      # Common components (Layout, etc.)
│   │   ├── admin/       # Admin-specific components
│   │   ├── teacher/     # Teacher-specific components
│   │   └── student/     # Student-specific components
│   ├── pages/           # Page components
│   │   ├── admin/       # Admin pages
│   │   ├── teacher/     # Teacher pages
│   │   └── student/     # Student pages
│   ├── services/        # API services
│   ├── store/           # Zustand stores
│   ├── types/           # TypeScript types
│   ├── utils/           # Utility functions
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies
```

## Pages and Routes

### Public Routes
- `/login` - Login page for all users
- `/parent-payment` - Parent payment portal

### Admin/Superuser Routes
- `/admin` - Dashboard with statistics
- `/admin/students` - Student management
- `/admin/groups` - Group management
- `/admin/contracts` - Contract management
- `/admin/payments` - Payment management
- `/admin/error-payments` - Error payment resolution
- `/admin/users` - User management (admin only)

### Teacher Routes
- `/teacher` - Teacher dashboard
- `/teacher/attendance` - Attendance marking

### Student Routes
- `/student` - Student dashboard
- `/student/payments` - Payment history
- `/student/attendance` - Attendance records

## Authentication

The app uses JWT token-based authentication:

1. User logs in with username/password
2. Backend returns JWT token and user info
3. Token is stored in localStorage
4. Token is automatically included in all API requests
5. User is redirected based on their role

### Login Credentials

**Students:**
- Username: `{enrollment_year}{student_id}` (e.g., `202410`)
- Default Password: Same as username

**Staff:**
- Use credentials provided by admin

## Features by Role

### Admin
- View system-wide statistics
- Manage students, groups, contracts
- View and manage all payments
- Resolve error payments
- Create and manage users
- Import students from Excel
- Generate reports

### Superuser
- Similar to admin but with configurable permissions
- Cannot manage other users
- Permissions assigned by admin

### Teacher
- View assigned groups
- Mark attendance for sessions
- View student list and information
- Track student payments and attendance

### Student
- View personal information
- Check payment history
- View attendance records
- See upcoming sessions

### Parent
- Enter contract number
- View student info and fees
- Make online payments via Payme/Click
- Get instant payment confirmation

## Styling

The app uses TailwindCSS for styling with a custom color scheme:

- Primary: Blue (#3b82f6)
- Success: Green (#10b981)
- Warning: Yellow (#f59e0b)
- Danger: Red (#ef4444)

## Development

### Adding a New Page

1. Create component in `src/pages/[role]/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/common/Layout.tsx`
4. Create necessary API service in `src/services/`

### Adding a New API Service

1. Create service file in `src/services/`
2. Use the `api` client from `src/services/api.ts`
3. Export functions for each endpoint
4. Use with React Query in components

## Environment Variables

- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting by route
- Lazy loading of components
- Optimized bundle size
- React Query caching

## Security

- JWT token authentication
- Role-based access control
- Protected routes
- Automatic token refresh
- Logout on token expiration

## Deployment

### Build

```bash
npm run build
```

### Preview Build

```bash
npm run preview
```

### Deploy

The built files in `dist/` can be deployed to any static hosting service:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront
- Azure Static Web Apps

## Troubleshooting

### API Connection Issues

1. Check if backend is running
2. Verify `VITE_API_URL` in `.env`
3. Check CORS settings in backend

### Build Errors

1. Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
2. Clear Vite cache: `rm -rf node_modules/.vite`
3. Update dependencies: `npm update`

## Support

For issues or questions, contact the development team.
