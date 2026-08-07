import axios from 'axios';
import type { GenerationRequest } from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 20000,
});

export async function startTextureGANGeneration(payload: GenerationRequest): Promise<any> {
  const form = new FormData();
  form.append('prompt', payload.prompt);
  form.append('primary_color', JSON.stringify(payload.primary_color));
  form.append('secondary_color', JSON.stringify(payload.secondary_color));
  if (payload.seed !== undefined && payload.seed !== null) form.append('seed', String(payload.seed));
  if (payload.num_samples !== undefined && payload.num_samples !== null) form.append('num_samples', String(payload.num_samples));
  // If reference_image is used: form.append('reference_image', payload.reference_image);
  // Do NOT set Content-Type manually! Let Axios/browser set it so the boundary is correct.
  const { data } = await api.post('/api/generate', form);
  return data;
}

export default api;
