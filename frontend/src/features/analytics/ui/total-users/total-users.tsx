import { ComponentPropsWithoutRef, FC } from 'react';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  count: number;
}

const TotalUsers: FC<IProps> = ({ className, count, ...props }) => {
  return (
    <div className={`flex-center ${className} p-6`} {...props}>
      <div className="text-center flex flex-col gap-6">
        <h1 className="text-ui-purple-primary font-bold text-[50px]">
          {count}
        </h1>
        <h2 className="text-sm text-gray-600 text-[20px]">
          Общее количество пользователей
        </h2>
      </div>
    </div>
  );
};

export default TotalUsers;
