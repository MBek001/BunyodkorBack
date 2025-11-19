import api from './api';
import { DashboardStats } from '@/types';

export const reportsService = {
  async getDashboard() {
    const response = await api.get<DashboardStats>('/api/reports/dashboard');
    return response.data;
  },

  async getMonthlyRevenue(year?: number) {
    const response = await api.get('/api/reports/revenue/monthly', { params: { year } });
    return response.data;
  },

  async getDebtors(params?: { skip?: number; limit?: number }) {
    const response = await api.get('/api/reports/debtors', { params });
    return response.data;
  },

  async getGroupStatistics(groupId: number) {
    const response = await api.get(`/api/reports/groups/${groupId}/statistics`);
    return response.data;
  },

  async getAttendanceSummary(params?: {
    start_date?: string;
    end_date?: string;
    group_id?: number;
  }) {
    const response = await api.get('/api/reports/attendance/summary', { params });
    return response.data;
  },
};
