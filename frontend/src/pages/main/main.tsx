import { useTokenStore } from '@/entities/admin';
import PageSwitcher from '@/features/page-switcher';
import { Header } from '@/shared/ui';
import { useNavigate } from 'react-router-dom';
import Content from './ui/content/content';

const MainPage = () => {
  const { logout } = useTokenStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex flex-col h-full">
      <Header onExit={handleLogout} />

      <div className="px-28 flex-1 overflow-hidden">
        <PageSwitcher />

        <Content />
      </div>
    </div>
  );
};

export default MainPage;

MainPage.url = '/telegram-admin';
MainPage.displayName = 'MainPage' as const;
