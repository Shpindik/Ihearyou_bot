import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001/api";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
