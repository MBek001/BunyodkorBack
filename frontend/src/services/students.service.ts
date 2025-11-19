import api from './api';
import { Student } from '@/types';

export const studentsService = {
  async getAll(params?: { skip?: number; limit?: number; group_id?: number; is_active?: boolean }) {
    const response = await api.get<Student[]>('/api/students', { params });
    return response.data;
  },

  async getById(id: number) {
    const response = await api.get<Student>(`/api/students/${id}`);
    return response.data;
  },

  async create(data: Partial<Student>) {
    const response = await api.post<Student>('/api/students', data);
    return response.data;
  },

  async update(id: number, data: Partial<Student>) {
    const response = await api.put<Student>(`/api/students/${id}`, data);
    return response.data;
  },

  async delete(id: number) {
    const response = await api.delete(`/api/students/${id}`);
    return response.data;
  },

  async importExcel(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/students/import-excel', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};
