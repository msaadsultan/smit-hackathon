'use client';

import { useEffect, useState } from 'react';
import { api } from '@/utils/api';

interface Stats {
  total_students: number;
  active_chats: number;
  total_conversations: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>({
    total_students: 0,
    active_chats: 0,
    total_conversations: 0,
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/stats');
        setStats(response.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };

    fetchStats();
  }, []);

  return (
    <div>
      <div className="pb-5 border-b border-gray-200">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Dashboard Overview
        </h3>
      </div>

      <dl className="mt-5 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="px-4 py-5 bg-white shadow rounded-lg overflow-hidden sm:p-6">
          <dt className="text-sm font-medium text-gray-500 truncate">
            Total Students
          </dt>
          <dd className="mt-1 text-3xl font-semibold text-gray-900">
            {stats.total_students}
          </dd>
        </div>

        <div className="px-4 py-5 bg-white shadow rounded-lg overflow-hidden sm:p-6">
          <dt className="text-sm font-medium text-gray-500 truncate">
            Active Chats
          </dt>
          <dd className="mt-1 text-3xl font-semibold text-gray-900">
            {stats.active_chats}
          </dd>
        </div>

        <div className="px-4 py-5 bg-white shadow rounded-lg overflow-hidden sm:p-6">
          <dt className="text-sm font-medium text-gray-500 truncate">
            Total Conversations
          </dt>
          <dd className="mt-1 text-3xl font-semibold text-gray-900">
            {stats.total_conversations}
          </dd>
        </div>
      </dl>
    </div>
  );
}