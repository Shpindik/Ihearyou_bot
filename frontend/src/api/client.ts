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

// Ratings API
export type ArticleRating = {
  id: number;
  fullname?: string | null;
  article_name: string;
  rating: number;
  created_at: string;
};

export type ArticleRatingSummaryItem = {
  article_name: string;
  ratings_count: number;
  avg_rating: number;
};

export const ratingsApi = {
  async list(): Promise<ArticleRating[]> {
    const res = await api.get<ArticleRating[]>("/article-ratings");
    return res.data;
  },
  async summary(): Promise<ArticleRatingSummaryItem[]> {
    const res = await api.get<ArticleRatingSummaryItem[]>("/article-ratings/summary");
    return res.data;
  },
};
