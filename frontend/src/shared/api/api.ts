import {errorInterceptor, requestInterceptor, successInterceptor,} from '@/shared/error-boundary/interceptors.ts';
import axios, {AxiosInstance, AxiosRequestConfig} from 'axios';

const axiosRequestConfig: AxiosRequestConfig = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001/api',
  responseType: 'json',
  headers: {
    'Content-Type': 'application/json',
    'X-App-Version': import.meta.env.APP_VERSION,
    'X-App-Type': import.meta.env.APP_TYPE,
  },
};

const api: AxiosInstance = axios.create(axiosRequestConfig);

api.interceptors.request.use(requestInterceptor);
api.interceptors.response.use(successInterceptor, errorInterceptor);

export { api };
