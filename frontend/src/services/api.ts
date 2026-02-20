/**
 * Axios API client with JWT token handling.
 *
 * Automatically attaches Bearer token to requests and handles
 * 401 responses by redirecting to login.
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: attach JWT token
api.interceptors.request.use(config => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Response interceptor: handle 401 unauthorized
api.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Try refreshing the token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken && !error.config._retry) {
        error.config._retry = true;
        try {
          const response = await axios.post(
            `${API_BASE_URL}/api/v1/auth/refresh`,
            null,
            { params: { refresh_token: refreshToken } }
          );
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          error.config.headers.Authorization = `Bearer ${access_token}`;
          return api(error.config);
        } catch {
          // Refresh failed — clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

// ==================== Auth API ====================

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post<User>('/auth/register', data),

  login: (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    return api.post<LoginResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },

  getMe: () => api.get<User>('/auth/me'),
};
