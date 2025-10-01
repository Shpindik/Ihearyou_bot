import {
  ComponentPropsWithoutRef,
  FC,
  ReactNode,
  useEffect,
  useState,
} from 'react';
import { createPortal } from 'react-dom';
import { CloseIcon } from '@/shared/svg';
import UIBlock from '../block';

interface IProps extends Omit<ComponentPropsWithoutRef<'div'>, 'title'> {
  open: boolean;
  onClose: () => void;
  closeButton?: boolean;
  title?: ReactNode;
  footer?: ReactNode;
}

const UIModal: FC<IProps> = ({
  open,
  onClose,
  closeButton = true,
  title,
  footer,
  children,
  className = '',
  ...props
}) => {
  const [animation, setAnimation] = useState(true);
  const [view, setView] = useState(false);

  useEffect(() => {
    setAnimation(open);

    if (open) {
      setView(true);
    }
  }, [open]);

  if (!view) return <></>;

  return createPortal(
    <div
      onClick={() => onClose()}
      className={`absolute inset-0 z-50 flex-center bg-ui-gray-bg-overlay backdrop-blur-sm ${animation ? 'animate-opacity-expand' : 'animate-opacity-collapse'}`}
      onAnimationEnd={() => {
        if (!animation) {
          setView(false);
        }
      }}
    >
      <UIBlock
        onClick={(e) => e.stopPropagation()}
        width=""
        padding=""
        className={`relative shadow-xl flex flex-col ${animation ? 'animate-slide-up' : 'animate-slide-down'} ${className}`}
        {...props}
      >
        <div className="flex-end">
          {!!title && (
            <div className="flex-1 text-center">
              <h1>{title}</h1>
            </div>
          )}

          {closeButton && (
            <div
              className={`flex-none w-12 h-12 flex-center ${!title ? 'absolute top-0 right-0' : ''}`}
            >
              <CloseIcon
                className="cursor-pointer text-ui-gray-text-secondary fine:hover:text-ui-gray-text-main transition-all"
                onClick={() => onClose()}
              />
            </div>
          )}
        </div>

        {children}

        {!!footer && footer}
      </UIBlock>
    </div>,
    document.body,
  );
};

export default UIModal;
