import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/common/Layout';
import api from '@/services/api';
import { ErrorPayment } from '@/types';

export default function ErrorPaymentsPage() {
  const { data: errorPayments, isLoading } = useQuery({
    queryKey: ['error-payments'],
    queryFn: async () => {
      const response = await api.get<ErrorPayment[]>('/api/payments/errors');
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <Layout title="Error Payments">
        <div className="text-center py-12">Loading...</div>
      </Layout>
    );
  }

  return (
    <Layout title="Error Payments">
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-900">
          Error Payments ({errorPayments?.length || 0})
        </h2>

        {errorPayments && errorPayments.length === 0 ? (
          <div className="bg-white shadow rounded-lg p-12 text-center">
            <p className="text-gray-500">No error payments found</p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Contract #
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Error Reason
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {errorPayments?.map((error: ErrorPayment) => (
                  <tr key={error.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {error.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {error.contract_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {error.amount.toLocaleString()} UZS
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {error.error_reason}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          error.is_resolved
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {error.is_resolved ? 'Resolved' : 'Pending'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {!error.is_resolved && (
                        <>
                          <button className="text-blue-600 hover:text-blue-900 mr-3">
                            Resolve
                          </button>
                          <button className="text-red-600 hover:text-red-900">Delete</button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
