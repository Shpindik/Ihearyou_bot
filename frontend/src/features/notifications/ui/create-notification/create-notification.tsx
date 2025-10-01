import { PlusIcon } from '@/shared/svg';
import UIBlock from '@/shared/ui/block/ui-block';
import { ComponentPropsWithoutRef, FC } from 'react';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  onClick: () => void;
}

const CreateNotification: FC<IProps> = ({
  onClick,
  className = '',
  ...props
}) => {
  return (
    <UIBlock
      className={`p-8 cursor-pointer hover:opacity-80 transition-opacity ${className}`}
      background="bg-ui-green-primary"
      onClick={onClick}
      {...props}
    >
      <div className="flex items-center justify-center gap-2 h-full w-full">
        <PlusIcon />

        <h2>создать уведомление</h2>
      </div>
    </UIBlock>
  );
};

export default CreateNotification;
