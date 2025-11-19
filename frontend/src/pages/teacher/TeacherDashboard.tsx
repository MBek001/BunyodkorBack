import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/common/Layout';
import api from '@/services/api';
import { useAuthStore } from '@/store/authStore';

export default function TeacherDashboard() {
  const { user } = useAuthStore();

  const { data: groups, isLoading } = useQuery({
    queryKey: ['teacher-groups'],
    queryFn: async () => {
      const response = await api.get('/api/groups', {
        params: { teacher_id: user?.id },
      });
      return response.data;
    },
  });

  const { data: sessions, isLoading: sessionsLoading } = useQuery({
    queryKey: ['teacher-sessions'],
    queryFn: async () => {
      const response = await api.get('/api/attendance/sessions');
      return response.data;
    },
  });

  if (isLoading || sessionsLoading) {
    return (
      <Layout title="Teacher Dashboard">
        <div className="text-center py-12">Loading...</div>
      </Layout>
    );
  }

  return (
    <Layout title="Teacher Dashboard">
      <div className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome, {user?.full_name}!</h2>
          <p className="text-gray-600">Manage your groups and track attendance</p>
        </div>

        {/* My Groups */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">My Groups</h3>
          {groups && groups.length > 0 ? (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {groups.map((group: any) => (
                <div key={group.id} className="border rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900">{group.name}</h4>
                  {group.description && (
                    <p className="text-sm text-gray-600 mt-1">{group.description}</p>
                  )}
                  <div className="mt-3 text-sm text-gray-500">
                    Max Students: {group.max_students}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No groups assigned yet</p>
          )}
        </div>

        {/* Recent Sessions */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Sessions</h3>
          {sessions && sessions.length > 0 ? (
            <div className="space-y-3">
              {sessions.slice(0, 5).map((session: any) => (
                <div
                  key={session.id}
                  className="flex justify-between items-center border-b pb-3"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      Session on {new Date(session.session_date).toLocaleDateString()}
                    </p>
                    <p className="text-sm text-gray-600">
                      {session.start_time} - {session.end_time}
                    </p>
                  </div>
                  <div>
                    <span
                      className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        session.is_completed
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {session.is_completed ? 'Completed' : 'Pending'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No sessions yet</p>
          )}
        </div>

        {/* Quick Actions */}
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <button className="px-4 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium">
              Mark Today's Attendance
            </button>
            <button className="px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm font-medium">
              View Student List
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
