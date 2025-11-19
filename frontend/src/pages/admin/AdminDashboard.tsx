import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/common/Layout';
import { reportsService } from '@/services/reports.service';

export default function AdminDashboard() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: reportsService.getDashboard,
  });

  if (isLoading) {
    return (
      <Layout title="Dashboard">
        <div className="text-center py-12">Loading...</div>
      </Layout>
    );
  }

  return (
    <Layout title="Dashboard">
      <div className="space-y-6">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {/* Total Students */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-1">
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Students</dt>
                  <dd className="mt-1 text-3xl font-semibold text-gray-900">
                    {stats?.students.total || 0}
                  </dd>
                  <dd className="mt-1 text-sm text-gray-600">
                    Active: {stats?.students.active || 0} | Inactive: {stats?.students.inactive || 0}
                  </dd>
                </div>
              </div>
            </div>
          </div>

          {/* Today's Revenue */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-1">
                  <dt className="text-sm font-medium text-gray-500 truncate">Today's Revenue</dt>
                  <dd className="mt-1 text-3xl font-semibold text-green-600">
                    {stats?.revenue.today.toLocaleString() || 0} UZS
                  </dd>
                </div>
              </div>
            </div>
          </div>

          {/* Monthly Revenue */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-1">
                  <dt className="text-sm font-medium text-gray-500 truncate">Monthly Revenue</dt>
                  <dd className="mt-1 text-3xl font-semibold text-blue-600">
                    {stats?.revenue.monthly.toLocaleString() || 0} UZS
                  </dd>
                </div>
              </div>
            </div>
          </div>

          {/* Debtors */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-1">
                  <dt className="text-sm font-medium text-gray-500 truncate">Debtors</dt>
                  <dd className="mt-1 text-3xl font-semibold text-red-600">
                    {stats?.debtors || 0}
                  </dd>
                  <dd className="mt-1 text-sm text-gray-600">
                    Students with unpaid fees
                  </dd>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Yearly Revenue */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Yearly Revenue</h3>
            <p className="text-4xl font-bold text-blue-600">
              {stats?.revenue.yearly.toLocaleString() || 0} UZS
            </p>
            <p className="text-sm text-gray-600 mt-2">Total revenue for {new Date().getFullYear()}</p>
          </div>
        </div>

        {/* Groups */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Groups</h3>
            <p className="text-2xl font-semibold text-gray-900">
              {stats?.groups.total || 0} Total Groups
            </p>
            <p className="text-sm text-gray-600 mt-1">
              Active: {stats?.groups.active || 0}
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <a
                href="/admin/students"
                className="inline-flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                Manage Students
              </a>
              <a
                href="/admin/payments"
                className="inline-flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                View Payments
              </a>
              <a
                href="/admin/groups"
                className="inline-flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-purple-600 hover:bg-purple-700"
              >
                Manage Groups
              </a>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
