import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for API calls to inject JWT Bearer Token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      let token = useAuthStore.getState().token;
      if (!token) {
        // Fallback to checking localStorage directly if Zustand state has not hydrated
        const authStorage = localStorage.getItem('auth-storage');
        if (authStorage) {
          try {
            const parsed = JSON.parse(authStorage);
            token = parsed?.state?.token;
          } catch (e) {
            console.error('Error parsing auth storage', e);
          }
        }
      }

      if (token && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle global errors (e.g. 401 Unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (typeof window !== 'undefined') {
        const currentPath = window.location.pathname;
        if (currentPath !== '/login' && currentPath !== '/') {
          useAuthStore.getState().logout();
        } else {
          localStorage.removeItem('auth-storage');
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
