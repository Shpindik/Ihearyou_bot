import Auth from '@/features/auth';
import {Header} from '@/shared/ui';

const LoginPage = () => {
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
