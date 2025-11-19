import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/common/Layout';
import api from '@/services/api';
import { useAuthStore } from '@/store/authStore';
import { format } from 'date-fns';

export default function StudentDashboard() {
  const { user } = useAuthStore();

  // Get student profile
  const { data: studentProfile, isLoading: profileLoading } = useQuery({
    queryKey: ['student-profile'],
    queryFn: async () => {
      const response = await api.get(`/api/students?user_id=${user?.id}`);
      return response.data[0]; // Assuming first result is the student
    },
  });

  // Get student payments
  const { data: payments, isLoading: paymentsLoading } = useQuery({
    queryKey: ['student-payments'],
    queryFn: async () => {
      if (!studentProfile) return [];
      const response = await api.get(`/api/payments?student_id=${studentProfile.id}`);
      return response.data;
    },
    enabled: !!studentProfile,
  });

  // Get student attendance
  const { data: attendance, isLoading: attendanceLoading } = useQuery({
    queryKey: ['student-attendance'],
    queryFn: async () => {
      if (!studentProfile) return [];
      const response = await api.get(`/api/attendance?student_id=${studentProfile.id}`);
      return response.data;
    },
    enabled: !!studentProfile,
  });

  if (profileLoading) {
    return (
      <Layout title="Student Dashboard">
        <div className="text-center py-12">Loading...</div>
      </Layout>
    );
  }

  return (
    <Layout title="Student Dashboard">
      <div className="space-y-6">
        {/* Profile Info */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Welcome, {studentProfile?.first_name}!
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Full Name</p>
              <p className="font-medium text-gray-900">
                {studentProfile?.first_name} {studentProfile?.last_name}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Enrollment Year</p>
              <p className="font-medium text-gray-900">{studentProfile?.enrollment_year}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Date of Birth</p>
              <p className="font-medium text-gray-900">
                {studentProfile?.date_of_birth
                  ? format(new Date(studentProfile.date_of_birth), 'MMM dd, yyyy')
                  : '-'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Parent Phone</p>
              <p className="font-medium text-gray-900">{studentProfile?.parent_phone}</p>
            </div>
          </div>
        </div>

        {/* Payment History */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment History</h3>
          {paymentsLoading ? (
            <p className="text-gray-500">Loading...</p>
          ) : payments && payments.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Date
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Amount
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Method
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {payments.slice(0, 5).map((payment: any) => (
                    <tr key={payment.id}>
                      <td className="px-4 py-2 text-sm text-gray-900">
                        {format(new Date(payment.payment_date), 'MMM dd, yyyy')}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-900">
                        {payment.amount.toLocaleString()} UZS
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-500 uppercase">
                        {payment.payment_method}
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            payment.payment_status === 'completed'
                              ? 'bg-green-100 text-green-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {payment.payment_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500">No payment history</p>
          )}
        </div>

        {/* Attendance Summary */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Attendance Summary</h3>
          {attendanceLoading ? (
            <p className="text-gray-500">Loading...</p>
          ) : attendance && attendance.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-green-50 rounded">
                <p className="text-2xl font-bold text-green-600">
                  {attendance.filter((a: any) => a.status === 'present').length}
                </p>
                <p className="text-sm text-gray-600">Present</p>
              </div>
              <div className="text-center p-4 bg-red-50 rounded">
                <p className="text-2xl font-bold text-red-600">
                  {attendance.filter((a: any) => a.status === 'absent').length}
                </p>
                <p className="text-sm text-gray-600">Absent</p>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded">
                <p className="text-2xl font-bold text-yellow-600">
                  {attendance.filter((a: any) => a.status === 'late').length}
                </p>
                <p className="text-sm text-gray-600">Late</p>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded">
                <p className="text-2xl font-bold text-blue-600">
                  {attendance.filter((a: any) => a.status === 'excused').length}
                </p>
                <p className="text-sm text-gray-600">Excused</p>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">No attendance records</p>
          )}
        </div>
      </div>
    </Layout>
  );
}
