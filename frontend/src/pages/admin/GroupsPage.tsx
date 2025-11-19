import { useQuery } from '@tanstack/react-query';
import Layout from '@/components/common/Layout';
import api from '@/services/api';
import { Group } from '@/types';

export default function GroupsPage() {
  const { data: groups, isLoading } = useQuery({
    queryKey: ['groups'],
    queryFn: async () => {
      const response = await api.get<Group[]>('/api/groups');
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <Layout title="Groups">
        <div className="text-center py-12">Loading...</div>
      </Layout>
    );
  }

  return (
    <Layout title="Groups Management">
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Groups ({groups?.length || 0})</h2>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Add Group
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {groups?.map((group: Group) => (
            <div key={group.id} className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900">{group.name}</h3>
              {group.description && (
                <p className="mt-1 text-sm text-gray-600">{group.description}</p>
              )}
              <div className="mt-4 space-y-2">
                <div className="text-sm text-gray-500">
                  Max Students: {group.max_students}
                </div>
                <div className="text-sm">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      group.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {group.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
              <div className="mt-4 flex gap-2">
                <button className="text-sm text-blue-600 hover:text-blue-900">Edit</button>
                <button className="text-sm text-red-600 hover:text-red-900">Delete</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  );
}
