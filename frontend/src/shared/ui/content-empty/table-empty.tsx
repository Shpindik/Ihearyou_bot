import { ComponentPropsWithoutRef, FC } from 'react';
import { CloseIcon } from '@/shared/svg';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  title?: string;
  text?: string;
  items: boolean;
}

const ContentEmpty: FC<IProps> = ({
  title,
  text,
  className = '',
  items,
  ...props
}) => {
  if (!items) return <></>;
  
  return (
    <div
      className={`flex-center flex-col gap-r-4 p-r-4 select-none min-h-96 ${className}`}
      {...props}
    >
      <CloseIcon className="text-ui-gray-text-secondary animate-pulse" />

      {!!title && <h1 className="font-ui text-r-lg text-ui-gray-text-main" />}

      {!!text && (
        <p className="slim text-ui-gray-text-secondary text-center">{text}</p>
      )}
    </div>
  );
};

export default ContentEmpty;
