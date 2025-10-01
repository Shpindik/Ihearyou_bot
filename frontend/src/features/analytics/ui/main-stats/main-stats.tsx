import { DailyViewDto } from '@/entities/analytics';
import { FC } from 'react';

interface IProps {
  totalUsers: number;
  newUsers: number;
  totalViews: number;
  averageViewsPerDay: number;
  dailyViews: DailyViewDto[];
}

const MainStats: FC<IProps> = ({
  totalUsers,
  newUsers,
  totalViews,
  averageViewsPerDay,
  dailyViews,
}) => {
  return (
    <div className="p-6">
      <div className="flex justify-between gap-[20%]">
        <div className="flex flex-col justify-between gap-4">
          <div>
            <h2 className="text-ui-purple-primary">{newUsers}</h2>
            <p>новых пользователей</p>
          </div>
          <div>
            <h2 className="text-ui-purple-primary">{totalUsers}</h2>
            <p>всего пользователей</p>
          </div>
          <div>
            <h2 className="text-ui-purple-primary">↑{totalViews}</h2>
            <p>всего просмотров</p>
          </div>
          <div>
            <h2 className="text-ui-purple-primary">{averageViewsPerDay}</h2>
            <p>в среднем просмотров в день</p>
          </div>
        </div>

        <div className="flex-1 max-w-[50%]">
          <div className="flex items-end justify-between px-4">
            {dailyViews.map((item, index) => {
              const max = Math.max(...dailyViews.map((d) => d.views));
              const height = (item.views / max) * 350;
              const colors = ['bg-ui-green-primary', 'bg-gray-300'];
              const style = colors[index % 2];

              return (
                <div
                  key={item.day}
                  className="flex flex-col items-center flex-1 "
                >
                  <div
                    className={`w-[40%] rounded-t-2xl ${style}`}
                    style={{ height: `${height}px` }}
                  />
                  <p>{item.day}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainStats;
