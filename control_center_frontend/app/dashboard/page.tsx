'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { controlAPI, authAPI } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const { user, setUser } = useAuthStore();

  useEffect(() => {
    const init = async () => {
      try {
        if (!user) {
          const { data } = await authAPI.me();
          setUser(data);
        }
        const { data } = await controlAPI.getDashboard();
        setMetrics(data);
      } catch (err) {
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };
    init();
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-purple-900 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">Sisi Lola Control Center</h1>
          <div className="flex items-center gap-4">
            <span>{user?.email}</span>
            <button onClick={authAPI.logout} className="bg-purple-700 px-4 py-2 rounded">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto p-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <MetricCard title="Total Assets" value={metrics?.assets?.total || 0} color="blue" />
          <MetricCard title="Pending Assets" value={metrics?.assets?.pending || 0} color="yellow" />
          <MetricCard title="Content Queue" value={metrics?.content?.queue_size || 0} color="green" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <ActionButton href="/dashboard/assets">Manage Assets</ActionButton>
              <ActionButton href="/dashboard/content">Content Queue</ActionButton>
              <ActionButton href="/dashboard/ml">ML Training</ActionButton>
              <ActionButton href="/dashboard/platforms">Platforms</ActionButton>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Your Roles</h2>
            <div className="flex flex-wrap gap-2">
              {user?.roles.map((role) => (
                <span key={role} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                  {role}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, color }: any) {
  const colors = {
    blue: 'bg-blue-500',
    yellow: 'bg-yellow-500',
    green: 'bg-green-500'
  };
  return (
    <div className={`${colors[color]} text-white p-6 rounded-lg shadow`}>
      <h3 className="text-lg opacity-90">{title}</h3>
      <p className="text-4xl font-bold mt-2">{value}</p>
    </div>
  );
}

function ActionButton({ href, children }: any) {
  return (
    <a href={href} className="block bg-purple-600 text-white p-3 rounded hover:bg-purple-700 text-center">
      {children}
    </a>
  );
}
