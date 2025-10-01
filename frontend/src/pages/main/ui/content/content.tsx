import {usePageStore} from '@/entities/page';
import AccessRights from '@/features/access-rights/access-rights.tsx';
import Analytics from '@/features/analytics/analytics.tsx';
import Materials from '@/features/materials';
import Notifications from '@/features/notifications';
import {ComponentPropsWithoutRef, FC} from 'react';

const Content: FC<ComponentPropsWithoutRef<'div'>> = ({
  className = '',
  ...props
}) => {
  const { state } = usePageStore();

  const renderContent = () => {
    switch (state) {
      case 'ANALYTICS':
        return <Analytics />;
      case 'MATERIALS':
        return <Materials />;
      case 'USERS_LIST':
        return <AccessRights />;
      case 'NOTIFICATIONS':
        return <Notifications />;
    }
  };

  return (
    <div className={`container-scroll w-full ${className}`} {...props}>
      {renderContent()}
    </div>
  );
};

export default Content;
