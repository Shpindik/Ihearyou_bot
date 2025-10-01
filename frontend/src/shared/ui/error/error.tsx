import {ComponentPropsWithoutRef, FC} from 'react';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  display?: boolean;
}

export const UIError: FC<IProps> = ({ className, children, display }) => {
  if (!display) {
    return null;
  }

  return (
    <div
      className={`text-red-500 text-sm text-center bg-red-50 p-2 rounded ${className}`}
    >
      {children}
    </div>
  );
};

export default UIError;
