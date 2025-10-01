import { api } from '@/shared/api';
import { IAnalyticsRequest } from '@/entities/analytics';
import { IAnalyticsResponse } from '@/entities/analytics';
import { analyticsMapper } from '@/entities/analytics';
import { TAnalyticsItem } from '@/entities/analytics/models/types/analytics-item.type';

export const getAnalytics = async (
  params?: IAnalyticsRequest,
): Promise<TAnalyticsItem | null> => {
  return api
    .get<IAnalyticsResponse>('/api/v1/admin/analytics', {
      baseURL: import.meta.env.VITE_API_URL,
      params,
    })
    .then((response) => response.data)
    .then(analyticsMapper);
};
