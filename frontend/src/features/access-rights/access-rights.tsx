import {
  getAdminList,
  TUserItem,
  userListMapper,
  userListMock,
} from '@/entities/user/list';
import { ComponentPropsWithoutRef, FC, useEffect, useState } from 'react';
import { AdminAccessRights } from './ui';

export const AccessRights: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  const [admins, setAdmins] = useState<TUserItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUsers = async () => {
      try {
        setLoading(true);
        const response = await getAdminList({ page: 1, limit: 20 });

        setAdmins(response.items);
        setTotal(response.total);
      } catch (error) {
        console.error(
          'Ошибка загрузки администраторов, используем моки:',
          error,
        );
        const mockData = userListMapper({ list: userListMock });
        setAdmins(mockData.items);
        setTotal(mockData.total);
      } finally {
        setLoading(false);
      }
    };

    void loadUsers();
  }, []);

  return (
    <div className={className}>
      <AdminAccessRights admins={admins} total={total} loading={loading} />
    </div>
  );
};

export default AccessRights;
