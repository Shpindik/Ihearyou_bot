import { MaterialAnalyticsDto } from '@/entities/analytics';
import { FC } from 'react';

interface IProps {
  materials: MaterialAnalyticsDto[];
}

const TopMaterials: FC<IProps> = ({ materials }) => {
  return (
    <div className="p-6 flex flex-col gap-4">
      <h2 className="mb-1">Топ-5 материалов по просмотрам</h2>

      {materials.slice(0, 5).map((material, index) => (
        <div key={material.id}>
          <p className="mb-1">
            {index + 1}. {material.title}
          </p>
          <div className="flex items-center gap-4">
            <div className="flex-1 h-8 bg-ui-gray-disabled rounded-full overflow-hidden">
              <div
                className="h-full bg-green-300 rounded-full transition-all duration-300"
                style={{ width: `${material.percentage}%` }}
              />
            </div>
            <p className="min-w-10 font-semibold">{material.percentage}%</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TopMaterials;
