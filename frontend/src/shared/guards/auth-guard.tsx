import { ComponentPropsWithoutRef, FC } from 'react';

const AuthGuard: FC<ComponentPropsWithoutRef<'div'>> = ({ children }) => {
  return <div>{children}</div>;
};

export default AuthGuard;
