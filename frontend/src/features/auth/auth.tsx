import { useTokenStore } from '@/entities/admin';
import { EyeShowIcon } from '@/shared/svg';
import { UIButton, UIError, UIInput } from '@/shared/ui';
import { ComponentPropsWithoutRef, FC, FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const Auth: FC<ComponentPropsWithoutRef<'div'>> = ({ className }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const { login } = useTokenStore();
  const navigate = useNavigate();

  const handleLogin = (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    login(username, password)
      .then(() => {
        navigate('/admin');
      })
      .catch((err) => {
        console.log(err);
        setError('Ошибка авторизации');
      })
      .finally(() => {
        setIsLoading(false);
      });
  };

  return (
    <form
      className={`flex-center flex-col gap-6 h-full w-full ${className}`}
      onSubmit={handleLogin}
    >
      <div className="flex flex-col gap-4 w-full max-w-96">
        <h1 className="mb-6 text-center">Вход</h1>

        <UIError display={!!error}>{error}</UIError>

        <UIInput
          placeholder="Логин"
          error={!!error}
          className="w-full"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value);
            setError('');
          }}
          required
        />

        <UIInput
          placeholder="Пароль"
          error={!!error}
          type="password"
          postfix={<EyeShowIcon />}
          className="w-full"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            setError('');
          }}
          required
        />

        <div className="flex-center flex-col gap-6 mt-4">
          <p className="text-center">Забыли пароль?</p>

          <UIButton
            theme="primary-fill"
            className="w-full"
            type="submit"
            disabled={isLoading}
          >
            {isLoading ? 'Вход...' : 'Войти'}
          </UIButton>
        </div>
      </div>
    </form>
  );
};

export default Auth;
