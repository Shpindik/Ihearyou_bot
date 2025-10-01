import { ComponentPropsWithoutRef, FC } from 'react';

export const Materials: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  return <div className={className}>Раздел Материалов</div>;
};

export default Materials;
