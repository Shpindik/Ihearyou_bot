import {ComponentPropsWithoutRef, FC, ReactNode} from 'react';
import {MSizes, MThemes, TSizes, TThemes} from './models';

interface IProps extends ComponentPropsWithoutRef<'button'> {
  theme?: TThemes;
  size?: TSizes;
  icon?: ReactNode;
}

const UIButton: FC<IProps> = ({
  theme = 'primary-fill',
  size = 'S',
  icon,
  className = '',
  children,
  ...props
}) => {
  return (
    <button
      className={`flex-center gap-2 select-none outline-none click-press rounded-full ${MSizes[size]} ${MThemes[theme]} ${className}`}
      {...props}
    >
      {!!icon && icon}

      {children}
    </button>
  );
};

export default UIButton;
