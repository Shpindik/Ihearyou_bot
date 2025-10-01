import {TUserItem} from '@/entities/user/list';
import {UsersCount} from '@/features/access-rights/ui/index.ts';
import {UIBlock, UIFullBackDropLoader} from '@/shared/ui';
import ContentEmpty from '@/shared/ui/content-empty/table-empty.tsx';
import {ComponentPropsWithoutRef, FC} from 'react';

interface UsersListProps extends ComponentPropsWithoutRef<'div'> {
  admins: TUserItem[];
  total: number;
  loading: boolean;
}

const UsersList: FC<UsersListProps> = ({
  className = '',
  admins,
  total,
  loading,
  ...props
}) => {
  return (
    <div className={`${className}`} {...props}>
      <UIFullBackDropLoader
        loading={loading}
        background={true}
        text="Загрузка администраторов..."
      />

      <h1>Список пользователей</h1>

      <div className="flex flex-col gap-4 w-full mt-10">
        {admins.map((admin) => (
          <UIBlock
            key={admin.id}
            className="flex p-6 justify-around rounded-full"
          >
            <p className="text-center">
              {admin.firstName} {admin.lastName}
            </p>

            <p className="text-center">{admin.username}</p>
          </UIBlock>
        ))}
        <UsersCount count={total} className="mt-4" />
      </div>

      <ContentEmpty
        title="Нет пользователей"
        text="Администраторы не найдены"
        items={!loading && admins.length === 0}
      />
    </div>
  );
};

export default UsersList;
