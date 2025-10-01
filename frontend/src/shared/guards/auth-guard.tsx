import { useTokenStore } from '@/entities/admin';
import { UIFullBackDropLoader } from '@/shared/ui';
import { PropsWithChildren, useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';

const AuthGuard = ({ children }: PropsWithChildren) => {
  const { token, refresh, logged } = useTokenStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (logged) return;

    if (token) {
      setLoading(true);

      refresh({ refresh_token: token.refresh })
        .then(() => {
          setError(false);
        })
        .catch(() => {
          setError(true);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setError(true);
    }
  }, [token, logged, refresh]);

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
