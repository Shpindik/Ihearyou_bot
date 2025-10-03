import { TAnalyticsItem } from '@/entities/analytics/models/types/analytics-item.type.ts';
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

        <UIBlock className="col-span-12 md:col-span-6">
          <TopMaterials materials={data.content.mostViewed} />
        </UIBlock>

        <UIBlock className="col-span-12">
          <MainStats
            materialsPercent={(() => {
              const totalViews = data.content.mostViewed.reduce(
                (sum, material) => sum + material.view_count,
                0,
              );
              const top5Views = data.content.mostViewed
                .slice(0, 5)
                .reduce((sum, material) => sum + material.view_count, 0);
              return totalViews > 0
                ? Math.round((top5Views / totalViews) * 100)
                : 0;
            })()}
            sectionsPercent={75}
          />
        </UIBlock>

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
