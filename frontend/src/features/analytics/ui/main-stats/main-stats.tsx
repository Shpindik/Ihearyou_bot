import { FC } from 'react';

interface IProps {
  percent: number;
}

const MainStats: FC<IProps> = ({ percent }) => {
  return (
    <div className="p-6">
      <div className="grid grid-cols-1 gap-6">
        <div className="text-center">
          <h2 className="text-ui-purple-primary text-2xl font-bold">
            {percent}%
          </h2>
          <p className="text-sm text-gray-600">
            От всех просмотров приходится на топ-5 материалов
          </p>
        </div>
      </div>
    </div>
  );
};

export default MainStats;
