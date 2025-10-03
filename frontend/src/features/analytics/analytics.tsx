import {
  analyticsMapper,
  analyticsMock,
  getAnalytics,
} from '@/entities/analytics';
import { TAnalyticsItem } from '@/entities/analytics/models/types/analytics-item.type';
import { usePageStore } from '@/entities/page';
import AnalyticsDashboard from '@/features/analytics/ui/analytics-dashboard.tsx';
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
  const { setLoading } = usePageStore();

  const loadAnalytics = useCallback(async () => {
    setLoading(true, 'Загрузка аналитики...');
    try {
      const data = await getAnalytics();
      setAnalyticsData(data);
    } catch (error) {
      console.error('Ошибка загрузки аналитики, используем моки:', error);
      setAnalyticsData(analyticsMapper(analyticsMock));
    } finally {
      setLoading(false);
    }
  }, [setLoading]);

  useEffect(() => {
    void loadAnalytics();
  }, [loadAnalytics]);

  return (
    <div className={`${className} w-full flex flex-col h-full`}>
      <div className="p-4">
        {/*Тут будет дродпаун*/}
        <h1>Статистика за моковый период</h1>
      </div>

      <div className="flex-1 min-h-0 overflow-auto scrollbar-hide">
        <div className="w-full">
          <AnalyticsDashboard data={analyticsData} />

          <ContentEmpty
            title="Нет данных"
            text="Не удалось загрузить данные аналитики"
            items={!analyticsData}
          />
        </div>
      </div>
    </div>
  );
};

export default Analytics;
