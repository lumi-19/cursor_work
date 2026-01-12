/**
 * THE_WORLD - API Service
 * Centralized API communication with backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Disasters API
export const disastersAPI = {
  getAll: (params?: any) => api.get('/disasters', { params }),
  getById: (id: number) => api.get(`/disasters/${id}`),
  getGeoJSON: (params?: any) => api.get('/disasters/geojson', { params }),
  getTypes: () => api.get('/disasters/types'),
};

// AQI API
export const aqiAPI = {
  getAll: (params?: any) => api.get('/aqi', { params }),
  getLatest: (params?: any) => api.get('/aqi/latest', { params }),
  getGeoJSON: (params?: any) => api.get('/aqi/geojson', { params }),
};

// Cities API
export const citiesAPI = {
  getAll: (params?: any) => api.get('/cities', { params }),
  getById: (id: number) => api.get(`/cities/${id}`),
};

// Comparison API
export const comparisonAPI = {
  compareAQI: (params: { city_ids: string; date?: string }) => 
    api.get('/comparison/aqi', { params }),
  compareHistorical: (params: { city_ids: string; start_date: string; end_date: string; interval?: string }) =>
    api.get('/comparison/aqi/historical', { params }),
};

// Correlation API
export const correlationAPI = {
  getDisasterAQI: (params?: any) => api.get('/correlation/disaster-aqi', { params }),
};

// Download API
export const downloadAPI = {
  disasters: (params: { format: string; [key: string]: any }) => 
    api.get('/download/disasters', { params, responseType: 'blob' }),
  aqi: (params: { format: string; [key: string]: any }) => 
    api.get('/download/aqi', { params, responseType: 'blob' }),
};

// Chatbot API
export const chatbotAPI = {
  sendMessage: (data: { message: string; conversation_id?: string; context?: any }) =>
    api.post('/chatbot/message', data),
  clearConversation: (data: { conversation_id: string }) =>
    api.post('/chatbot/clear', data),
};

// Health check
export const healthCheck = () => axios.get(`${API_BASE_URL.replace('/api', '')}/api/health`);

export default api;
