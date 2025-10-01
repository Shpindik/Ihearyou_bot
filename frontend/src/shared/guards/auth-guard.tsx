import {useTokenStore} from '@/entities/admin';
import {UIFullBackDropLoader} from '@/shared/ui';
import {PropsWithChildren, useEffect, useState} from 'react';
import {Navigate} from 'react-router-dom';

const AuthGuard = ({ children }: PropsWithChildren) => {
  const dev = import.meta.env.DEV && localStorage.getItem('DEV_BYPASS') === '1';
  //ON: localStorage.setItem('DEV_BYPASS', '1'); location.reload();
  //OFF: localStorage.removeItem('DEV_BYPASS'); location.reload();

  const { token, refresh, logged } = useTokenStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  if (dev) return <>{children}</>;

  useEffect(() => {
    if (logged || dev) return;

    if (token) {
      setLoading(true);
      refresh({ refresh_token: token.refresh })
        .then(() => setError(false))
        .catch(() => setError(true))
        .finally(() => setLoading(false));
    } else {
      setError(true);
    }
  }, [token, logged, refresh, dev]);

  if (loading)
    return (
      <div className="full-size relative">
        <UIFullBackDropLoader
          text="Аутентификация..."
          background={true}
          block={true}
        />
      </div>
    );

  if (error || !logged) return <Navigate to={'/login'} replace />;

  return <>{children}</>;
};

export default AuthGuard;
