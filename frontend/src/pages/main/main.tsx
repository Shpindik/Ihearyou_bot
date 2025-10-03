import { useTokenStore } from '@/entities/admin';
import { usePageStore } from '@/entities/page';
import PageSwitcher from '@/features/page-switcher';
import { Header, UIFullBackDropLoader } from '@/shared/ui';
import { useNavigate } from 'react-router-dom';
import Content from './ui/content/content';

const MainPage = () => {
  const { logout } = useTokenStore();
  const { loading, loadingText } = usePageStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex flex-col h-screen">
      <Header onExit={handleLogout} />

      <div className="px-[5%] flex-1 flex flex-col min-h-0">
        <PageSwitcher />

        <Content />
      </div>

      <UIFullBackDropLoader
        loading={loading}
        background={true}
        className="fixed inset-0 z-50"
        text={loadingText}
      />
    </div>
  );
};

export default MainPage;

MainPage.url = '/telegram-admin';
MainPage.displayName = 'MainPage' as const;
