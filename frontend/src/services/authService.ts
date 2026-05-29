import api from './api';
import { AuthResponse } from '../types';

export const authService = {
  async login(mobile: string, password: string): Promise<AuthResponse> {
    const response = await api.post('/auth/login', { mobile, password });
    return response.data;
  },

  async register(data: {
    mobile: string;
    password: string;
    first_name: string;
    last_name: string;
    address: string;
    city: string;
    state: string;
    zip_code: string;
    email?: string;
  }): Promise<AuthResponse> {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  async getProfile() {
    const response = await api.get('/auth/profile');
    return response.data;
  },

  async updateProfile(data: {
    first_name?: string;
    last_name?: string;
    address?: string;
    city?: string;
    state?: string;
    zip_code?: string;
  }) {
    const response = await api.put('/auth/profile', data);
    return response.data;
  },

  async getStatus() {
    const response = await api.get('/auth/status');
    return response.data;
  },
};
