import { MaterialAnalyticsDto } from '@/entities/analytics';
import { FC } from 'react';

interface IProps {
  materials: MaterialAnalyticsDto[];
}

const TopMaterials: FC<IProps> = ({ materials }) => {
  if (!materials || materials.length === 0) {
    return (
      <div className="p-6 flex flex-col gap-4">
        <h2 className="mb-1">Топ-5 материалов по просмотрам</h2>
        <p>Здесь пока ничего нет</p>
      </div>
    );
  }

  return (
    <div className="p-6 flex flex-col gap-4">
      <h2 className="mb-1">Топ-5 материалов по просмотрам</h2>

      {materials.slice(0, 5).map((material, index) => {
        const maxViews = Math.max(...materials.map((m) => m.view_count));
        const percentage = (material.view_count / maxViews) * 100;

        return (
          <div key={material.id}>
            <p className="mb-1">
              {index + 1}. {material.title}
            </p>
            <div className="flex items-center gap-4">
              <div className="flex-1 h-8 bg-ui-gray-disabled rounded-full overflow-hidden">
                <div
                  className="h-full bg-ui-green-primary rounded-full transition-all duration-300"
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <p className="min-w-10 font-semibold">{material.view_count}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default TopMaterials;
