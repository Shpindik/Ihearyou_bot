import { MaterialRatingDto } from '@/entities/analytics';
import { FC } from 'react';

interface IProps {
  materials: MaterialRatingDto[];
}

const TopRatings: FC<IProps> = ({ materials }) => {
  if (!materials || materials.length === 0) {
    return (
      <div className="p-6 flex flex-col gap-4">
        <h2 className="mb-1">Топ-5 материалов по оценке</h2>
        <p>Здесь пока ничего нет</p>
      </div>
    );
  }

  return (
    <div className="p-6 flex flex-col gap-4">
      <h2 className="mb-1">Топ-5 материалов по оценке</h2>

      {materials.slice(0, 5).map((material, index) => (
        <div key={material.id}>
          <p className="mb-1">
            {index + 1}. {material.title}
          </p>

          <div className="flex items-center gap-4">
            <div className="flex-1 h-8 bg-ui-gray-disabled rounded-full overflow-hidden">
              <div
                className="h-full bg-ui-green-primary rounded-full transition-all duration-300"
                style={{ width: `${(material.average_rating / 5) * 100}%` }}
              />
            </div>

            <p className="min-w-16 font-semibold">
              {material.average_rating.toFixed(1)}/5.0
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default TopRatings;
