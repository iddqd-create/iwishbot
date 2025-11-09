
import axios from 'axios';
import WebApp from '@twa-dev/sdk';

const API_URL = `${window.location.origin}/api`;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-Telegram-Init-Data': WebApp.initData || '',
  },
});

export default api;
