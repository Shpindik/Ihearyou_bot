import { ComponentPropsWithoutRef, FC } from 'react';
import { EErrors } from '@/pages/error/ui/models';
import { LopeCloseIcon, CrossCircleIcon } from '@/shared/svg';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  error: EErrors;
}

const Icon: FC<IProps> = ({ className, error, ...props }) => {
  const renderContent = () => {
    switch (error) {
      case EErrors.NOT_FOUND:
        return <LopeCloseIcon className="w-12 h-12" />;
      case EErrors.NOT_AUTHORIZED:
        return <CrossCircleIcon className="w-12 h-12" />;
      default:
        return <></>;
    }
  };

  return (
    <div className={`${className}`} {...props}>
      {renderContent()}
    </div>
  );
};

export default Icon;
