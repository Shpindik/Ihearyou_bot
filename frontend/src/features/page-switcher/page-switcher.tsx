import { usePageStore } from '@/entities/page';
import UIButton from '@/shared/ui/button';
import { ComponentPropsWithoutRef, FC } from 'react';
import { MLabels, MOrder } from './models/maps/tabs.map';

const PageSwitcher: FC<ComponentPropsWithoutRef<'div'>> = ({
  className = '',
  ...props
}) => {
  const { state, setState } = usePageStore();

  return (
    <div
      className={`flex items-center w-full gap-4 py-16 ${className}`}
      {...props}
    >
      {MOrder.map((value) => (
        <UIButton
          key={value}
          theme="none"
          size="S"
          className={`text-white ${state === value ? 'bg-ui-purple-primary' : 'bg-ui-purple-disabled'}`}
          onClick={() => setState(value)}
        >
          {MLabels[value]}
        </UIButton>
      ))}
    </div>
  );
};

export default PageSwitcher;
