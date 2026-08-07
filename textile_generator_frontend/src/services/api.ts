import axios from 'axios';
import type { GenerationRequest, GenerationStatus, StyleOption, ApiHealth } from '../types';

// Add Vite importMetaEnv type declaration if missing
interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 20000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
    }
    if (error.response?.data?.error) {
      return Promise.reject(new Error(error.response.data.error));
    }
    return Promise.reject(error);
  },
);

export async function getHealth(): Promise<ApiHealth> {
  const { data } = await api.get('/api/health');
  return data;
}

export async function getStyles(): Promise<StyleOption[]> {
  const { data } = await api.get('/api/styles');
  return data.styles;
}

export async function startGeneration(payload: GenerationRequest): Promise<GenerationStatus> {
  // Log outgoing payload for debugging
  console.log('[API] startGeneration payload:', payload);
  try {
    const { data } = await api.post('/api/generate', payload, {
      headers: { 'Content-Type': 'application/json' },
    });
    return data.generation;
  } catch (error: any) {
    if (error.response) {
      console.error('[API] /api/generate error:', error.response.status, error.response.data);
    } else {
      console.error('[API] /api/generate error:', error);
    }
    throw error;
  }
}

export async function getGenerationStatus(id: number): Promise<GenerationStatus> {
  const { data } = await api.get(`/api/status/${id}`);
  return data.generation;
}

export async function getHistory(limit = 10, offset = 0): Promise<GenerationStatus[]> {
  const { data } = await api.get('/api/history', { params: { limit, offset } });
  return data.generations;
}

export async function login(username: string, password: string): Promise<string> {
  const { data } = await api.post('/api/login', { username, password });
  return data.access_token;
}

export async function register(username: string, email: string, password: string): Promise<void> {
  await api.post('/api/register', { username, email, password });
}

export default api;
