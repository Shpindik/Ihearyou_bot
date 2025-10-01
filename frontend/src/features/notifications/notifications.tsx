import { ComponentPropsWithoutRef, FC } from 'react';

export const Notifications: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  return <div className={className}>Раздел Уведомлений</div>;
};

export default Notifications;
