import {analyticsMapper, IAnalyticsRequest, IAnalyticsResponse, TAnalyticsItem,} from '@/entities/analytics';
import {api} from '@/shared/api';

export const getAnalytics = async (
  params?: IAnalyticsRequest,
): Promise<TAnalyticsItem | null> => {
  return api
    .get<IAnalyticsResponse>('/v1/admin/analytics', {
      params,
    })
    .then((response) => {
      return response.data;
    })
    .then(analyticsMapper)
    .catch((e) => {
      console.log(e);
      throw e;
    });
};
