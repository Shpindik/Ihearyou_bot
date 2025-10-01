import { ComponentPropsWithoutRef, FC } from 'react';

export const AccessRights: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  return <div className={className}>Раздел аналитики</div>;
};

export default AccessRights;
