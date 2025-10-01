import { FC } from 'react';

interface IProps {
  materialsPercent: number;
  sectionsPercent: number;
}

const MainStats: FC<IProps> = ({ materialsPercent, sectionsPercent }) => {
  return (
    <div className="p-6">
      <div className="grid grid-cols-2 gap-6">
        <div className="text-center">
          <h2 className="text-ui-purple-primary text-2xl font-bold">
            {materialsPercent}%
          </h2>
          <p className="text-sm text-gray-600">
            От всех просмотров приходится на топ-5 материалов
          </p>
        </div>

        <div className="text-center">
          <h2 className="text-ui-purple-primary text-2xl font-bold">
            {sectionsPercent}%
          </h2>
          <p className="text-sm text-gray-600">
            От всех просмотров приходится на топ-5 разделов
          </p>
        </div>
      </div>
    </div>
  );
};

export default MainStats;
