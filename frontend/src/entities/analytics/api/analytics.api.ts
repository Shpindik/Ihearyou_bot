import { api } from '@/shared/api';
import { analyticsMock } from '../mocks/analytics-mock';
import { IAnalyticsRequest } from '../models/interfaces/analytics-request.interface';
import { IAnalyticsResponse } from '../models/interfaces/analytics-response.interface';
import { analyticsMapper } from '../models/mappers/analytics.mapper';
import { TAnalyticsItem } from '../models/types/analytics-item.type';

// Флаг для переключения между API и моками
const USE_MOCKS = true;

export const getAnalytics = async (
  params?: IAnalyticsRequest,
): Promise<TAnalyticsItem | null> => {
  if (USE_MOCKS) {
    console.log('Используем мок данные для аналитики');
    return Promise.resolve(analyticsMapper(analyticsMock));
  }

  return api
    .get<IAnalyticsResponse>('/api/v1/admin/analytics', {
      params,
    })
    .then((response) => {
      console.log('API ответ:', response.data);
      return response.data;
    })
    .then(analyticsMapper)
    .catch((error) => {
      console.log('Ошибка API:', error);
      throw error;
    });
};
