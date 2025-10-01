import { useTokenStore } from '@/entities/admin';
import { Header } from '@/shared/ui';
import { useNavigate } from 'react-router-dom';

const MainPage = () => {
  const { logout } = useTokenStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="container-main p-r-4 gap-r-4">
      <Header onExit={handleLogout} />
      <div>Главная страница</div>
    </div>
  );
};

export default MainPage;

MainPage.url = '/telegram-admin';
MainPage.displayName = 'MainPage' as const;
