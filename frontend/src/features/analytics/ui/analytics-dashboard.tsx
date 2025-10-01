import { TAnalyticsItem } from '@/entities/analytics/models/types/analytics-item.type.ts';
import { UIBlock } from '@/shared/ui';
import {
  AntiTopRatings,
  MainStats,
  TopMaterials,
  TopRatings,
  TopSummary,
  TopViews,
} from './index.ts';

interface AnalyticsDashboardProps {
  data: TAnalyticsItem;
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ data }) => {
  if (!data) {
    return null;
  }

  return (
    <div className="p-6 pb-48">
      <div className="grid grid-cols-12 gap-6">
        {/* Основная статистика */}
        <UIBlock className="col-span-12">
          <MainStats
            totalUsers={data.users.total}
            newUsers={data.users.newUsers}
            totalViews={data.content.totalViews}
            averageViewsPerDay={data.content.averageViewsPerDay}
            dailyViews={data.dailyViews}
          />
        </UIBlock>

        {/* Топ материалы и разделы */}
        <UIBlock className="col-span-12 md:col-span-6">
          <TopMaterials materials={data.content.topMaterials} />
        </UIBlock>

        <UIBlock className="col-span-12 md:col-span-6">
          <TopViews sections={data.content.topSections} />
        </UIBlock>

        {/* Сводка */}
        <UIBlock className="col-span-12">
          <TopSummary
            materials={data.content.topMaterials}
            sections={data.content.topSections}
          />
        </UIBlock>

        {/* Рейтинги */}
        <UIBlock className="col-span-12 md:col-span-6">
          <TopRatings materials={data.ratings.topMaterials} />
        </UIBlock>

        <UIBlock className="col-span-12 md:col-span-6">
          <AntiTopRatings materials={data.ratings.antiTopMaterials} />
        </UIBlock>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
