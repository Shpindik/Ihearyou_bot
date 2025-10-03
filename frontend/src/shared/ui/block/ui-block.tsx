import {ComponentPropsWithoutRef, FC} from 'react';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  padding?: string;
  width?: string;
  rounded?: string;
  background?: string;
}

const UIBlock: FC<IProps> = ({
  padding = 'p-r-4',
  width = 'w-full',
  rounded = 'rounded-2xl',
  background = 'bg-ui-purple-secondary',
  className = '',
  children,
  ...props
}) => {
  return (
    <div
      className={`${padding} ${width} ${rounded} ${background} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export default UIBlock;
