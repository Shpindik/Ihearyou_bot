import {ComponentPropsWithoutRef, FC} from 'react';
import {UIBlock} from '@/shared/ui';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  count: number;
}

const UsersCount: FC<IProps> = ({ count, className }) => {
  if (!count) {
    return null;
  }

  return (
    <UIBlock className={`p-8 ${className}`}>
      <div className="flex-center">
        <div className="text-center">
          <h2 className="text-ui-purple-primary text-2xl font-bold">{count}</h2>
          <p className="text-sm text-gray-600">
            Общее количество пользователей
          </p>
        </div>
      </div>
    </UIBlock>
  );
};

export default UsersCount;
