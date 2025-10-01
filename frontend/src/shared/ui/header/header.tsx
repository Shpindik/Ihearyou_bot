import { useTokenStore } from '@/entities/admin';
import ExitButton from '@/shared/ui/header/ui/exit-button.tsx';
import { ComponentPropsWithoutRef, FC } from 'react';
import MainLogo from '../../../../public/logo.svg';

interface IHeaderProps extends ComponentPropsWithoutRef<'div'> {
  onExit?: () => void;
}

export const Header: FC<IHeaderProps> = ({ className, onExit }) => {
  const { logged } = useTokenStore();

  return (
    <div
      className={`w-screen mh-20% bg-ui-purple-tertiary py-5 px-28 flex justify-between ${className}`}
    >
      <img
        src={MainLogo}
        alt="Главное лого"
        className="self-center w-15 h-15"
      />
      <ExitButton display={logged} onExit={onExit} />
    </div>
  );
};

export default Header;
