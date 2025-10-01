import { getAnalytics } from '@/entities/analytics';
import { TAnalyticsItem } from '@/entities/analytics/models/types/analytics-item.type';
import AnalyticsDashboard from '@/features/analytics/ui/analytics-dashboard.tsx';
import FullBackdropLoader from '@/shared/ui/full-backdrop-loader';
import { ComponentPropsWithoutRef, FC, useEffect, useState } from 'react';

export const Analytics: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  const [analyticsData, setAnalyticsData] = useState<TAnalyticsItem | null>(
    null,
  );
  const [loading, setLoading] = useState(false);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const data = await getAnalytics();
      setAnalyticsData(data);
    } catch (error) {
      console.error('Ошибка загрузки аналитики:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadAnalytics();
  }, []);

  return (
    <div className={`${className} w-full relative`}>
      <div className="w-full pb-8">
        {/*Тут будет дродпаун*/}

        <h1>Статистика за моковый период</h1>

        <AnalyticsDashboard data={analyticsData} />
      </div>

      <FullBackdropLoader
        text="Загрузка аналитики..."
        background
        block
        loading={loading}
      />
    </div>
  );
};

export default Analytics;
