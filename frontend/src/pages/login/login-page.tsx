import { UIInput } from '@/shared/ui';

const LoginPage = () => {
  return (
    <div>
      <UIInput />
      <div>Страница входа</div>
    </div>
  );
};

export default LoginPage;

LoginPage.url = '/login';
LoginPage.displayName = 'LoginPage' as const;
