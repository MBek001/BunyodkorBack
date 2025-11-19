import { ReactNode } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

interface LayoutProps {
  children: ReactNode;
  title: string;
}

export default function Layout({ children, title }: LayoutProps) {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getNavLinks = () => {
    if (!user) return [];

    switch (user.role) {
      case 'admin':
      case 'superuser':
        return [
          { path: '/admin', label: 'Dashboard' },
          { path: '/admin/students', label: 'Students' },
          { path: '/admin/groups', label: 'Groups' },
          { path: '/admin/contracts', label: 'Contracts' },
          { path: '/admin/payments', label: 'Payments' },
          { path: '/admin/error-payments', label: 'Error Payments' },
          ...(user.role === 'admin' ? [{ path: '/admin/users', label: 'Users' }] : []),
        ];
      case 'teacher':
        return [
          { path: '/teacher', label: 'Dashboard' },
          { path: '/teacher/attendance', label: 'Attendance' },
        ];
      case 'student':
        return [
          { path: '/student', label: 'Dashboard' },
          { path: '/student/payments', label: 'Payments' },
          { path: '/student/attendance', label: 'Attendance' },
        ];
      default:
        return [];
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Bunyodkor CIMS</h1>
              <p className="text-sm text-gray-600">{title}</p>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700">
                {user?.full_name || user?.username} ({user?.role})
              </span>
              <button
                onClick={handleLogout}
                className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-4 py-3">
            {getNavLinks().map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className="rounded-md px-3 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white"
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  );
}
