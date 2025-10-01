import { ComponentPropsWithoutRef, FC } from 'react';

export const Header: FC<ComponentPropsWithoutRef<'div'>> = ({ className }) => {
  return <div className={`w-screen bg-ui-purple-tertiary ${className}`}></div>;
};
