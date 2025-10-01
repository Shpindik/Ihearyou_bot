import { ComponentPropsWithoutRef, FC, } from 'react';

export const Analytics: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  return <div className={className}>Раздел аналитики</div>;
};

export default Analytics;
