import {ExitIcon} from '@/shared/svg';
import {UIButton} from '@/shared/ui';
import {ComponentPropsWithoutRef, FC} from 'react';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  display?: boolean;
  onExit?: () => void;
}

const ExitButton: FC<IProps> = ({ className, display, onExit }) => {
  if (!display) {
    return null;
  }

  return (
    <UIButton
      className={`${className} text-ui-gray-text-additional`}
      theme="none"
      onClick={onExit}
    >
      <ExitIcon />
    </UIButton>
  );
};

export default ExitButton;
