import {
  analyticsMapper,
  getAnalytics,
  IAnalyticsRequest,
} from '@/entities/analytics';
import { getAnalyticsMock } from '@/entities/analytics/mocks';
import { TAnalyticsItem } from '@/entities/analytics/models/types/analytics-item.type';
import { AnalyticsFilter } from '@/features/analytics/ui';
import AnalyticsDashboard from '@/features/analytics/ui/analytics-dashboard.tsx';
import { UIFullBackDropLoader } from '@/shared/ui';
import ContentEmpty from '@/shared/ui/content-empty/table-empty.tsx';
import {
  ComponentPropsWithoutRef,
  FC,
  useCallback,
  useEffect,
  useState,
} from 'react';

export const Analytics: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  const [analyticsData, setAnalyticsData] = useState<TAnalyticsItem | null>(
    null,
  );
  const [loading, setLoading] = useState(false);

  const loadAnalytics = useCallback((params?: IAnalyticsRequest) => {
    setLoading(true);

    return getAnalytics(params)
      .then((data) => {
        setAnalyticsData(data);
        return data;
      })
      .catch((error) => {
        console.error(error);
        // MOCK
        const mockData = getAnalyticsMock(params?.period);
        const mappedData = analyticsMapper(mockData);
        setAnalyticsData(mappedData);
        return mappedData;
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const handleFilterChange = useCallback(
    (newFilters: IAnalyticsRequest) => {
      void loadAnalytics(newFilters);
    },
    [loadAnalytics],
  );

  useEffect(() => {
    void loadAnalytics();
  }, [loadAnalytics]);

  return (
    <div className={`${className} w-full flex flex-col h-full`}>
      <div className="p-4">
        <div className="flex gap-2 items-center justify-between mb-4">
          <h1>Статистика</h1>
          <AnalyticsFilter onFilterChange={handleFilterChange} />
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-auto scrollbar-hide">
        <div className="w-full">
          <AnalyticsDashboard data={analyticsData} />

          <ContentEmpty
            title="Нет данных"
            text="Не удалось загрузить данные аналитики"
            items={!analyticsData && !loading}
          />
        </div>
      </div>

      <UIFullBackDropLoader loading={loading} text="Загрузка аналитики..." />
    </div>
  );
};

export default Analytics;
