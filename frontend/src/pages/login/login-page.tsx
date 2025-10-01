import { useTokenStore } from '@/entities/admin';
import Auth from '@/features/auth';
import { Header } from '@/shared/ui';
import { Navigate } from 'react-router-dom';

const LoginPage = () => {
  const { logged } = useTokenStore();

  if (logged) {
    return <Navigate to="/admin" replace />;
  }

  return (
    <div className="container-main">
      <Header />
      <Auth />
    </div>
  );
};

export default LoginPage;

LoginPage.url = '/login';
LoginPage.displayName = 'LoginPage' as const;
