import { TAnalyticsItem } from '@/entities/analytics/models/types/analytics-item.type.ts';
import TotalUsers from '@/features/analytics/ui/total-users/total-users.tsx';
import { UIBlock } from '@/shared/ui';
import { FC } from 'react';
import {
  AntiTopRatings,
  MainStats,
  TopMaterials,
  TopRatings,
} from './index.ts';

interface AnalyticsDashboardProps {
  data: TAnalyticsItem;
}

const AnalyticsDashboard: FC<AnalyticsDashboardProps> = ({ data }) => {
  if (!data) {
    return null;
  }

  return (
    <div className="px-6">
      <div className="grid grid-cols-12 gap-6">
        <UIBlock className="col-span-12 md:col-span-6">
          <TopMaterials materials={data.content.mostViewed} />
        </UIBlock>

        <div className="col-span-12 md:col-span-6 flex flex-col gap-2">
          <UIBlock className="h-full flex-center">
            <TotalUsers count={data.users.total} className="m-auto" />
          </UIBlock>

          <UIBlock>
            <MainStats
              percent={(() => {
                const total = data.content.mostViewed.reduce(
                  (sum, material) => sum + material.view_count,
                  0,
                );
                const top = data.content.mostViewed
                  .slice(0, 5)
                  .reduce((sum, material) => sum + material.view_count, 0);
                return total > 0 ? Math.round((top / total) * 100) : 0;
              })()}
            />
          </UIBlock>
        </div>

        <UIBlock className="col-span-12 md:col-span-6">
          <TopRatings materials={data.content.mostRated} />
        </UIBlock>

        <UIBlock className="col-span-12 md:col-span-6">
          <AntiTopRatings
            materials={data.content.mostRated.filter(
              (material) => material.average_rating < 3.0,
            )}
          />
        </UIBlock>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
