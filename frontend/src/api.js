// src/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';  // Backend adresin

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// HER İSTEKTE TOKEN'I HEADER'A EKLE
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      // Debug (kaldırabilirsin)
      console.log('API isteği gönderiliyor → Token:', token.substring(0, 20) + '...');
    } else {
      // Token yoksa header'ı temizle
      delete config.headers.Authorization;
      console.log('API isteği gönderiliyor → Token YOK');
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// YANITLARDA 401/403 ALIRSAK OTOMATİK LOGOUT
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.warn('Token geçersiz veya yetkisiz erişim → Logout yapılıyor');
      localStorage.removeItem('access_token');
      window.location.href = '/auth';  // Tam reload ile auth sayfasına git
    }
    return Promise.reject(error);
  }
);

export default api;