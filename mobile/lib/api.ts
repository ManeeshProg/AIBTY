import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// Change this to your backend URL
// For Android emulator use 10.0.2.2 instead of localhost
const API_URL = 'http://10.0.2.2:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token storage keys
const TOKEN_KEY = 'auth_token';

// Token management
export const getToken = async (): Promise<string | null> => {
  return await SecureStore.getItemAsync(TOKEN_KEY);
};

export const setToken = async (token: string): Promise<void> => {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
};

export const removeToken = async (): Promise<void> => {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
};

// Add auth header to requests
api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authApi = {
  register: async (email: string, password: string, fullName?: string) => {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  login: async (email: string, password: string) => {
    // Login uses form data (OAuth2PasswordRequestForm)
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Journal API
export const journalApi = {
  getToday: async () => {
    const today = new Date().toISOString().split('T')[0];
    const response = await api.get(`/journals/${today}`);
    return response.data;
  },

  create: async (date: string, content: string) => {
    const response = await api.post('/journals/', { date, content });
    return response.data;
  },

  update: async (date: string, content: string) => {
    const response = await api.put(`/journals/${date}`, { content });
    return response.data;
  },
};

// Scores API
export const scoresApi = {
  getToday: async () => {
    const response = await api.get('/scores/today');
    return response.data;
  },

  score: async () => {
    const response = await api.post('/scores/score');
    return response.data;
  },
};

// Verdicts API
export const verdictsApi = {
  getToday: async () => {
    const response = await api.get('/verdicts/today');
    return response.data;
  },

  generate: async () => {
    const response = await api.post('/verdicts/generate');
    return response.data;
  },
};

// Goals API
export const goalsApi = {
  getAll: async () => {
    const response = await api.get('/goals/');
    return response.data;
  },

  create: async (category: string, description: string, weight?: number) => {
    const response = await api.post('/goals/', { category, description, weight });
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/goals/${id}`);
  },

  getSuggestions: async () => {
    const response = await api.get('/goals/suggestions');
    return response.data;
  },
};

// Trends API
export const trendsApi = {
  getAll: async () => {
    const response = await api.get('/trends/');
    return response.data;
  },

  getByCategory: async (category: string) => {
    const response = await api.get(`/trends/${category}`);
    return response.data;
  },
};

export default api;
