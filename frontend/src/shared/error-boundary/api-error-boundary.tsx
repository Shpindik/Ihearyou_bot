import { api } from '@/shared/api/api.ts';
import { TRequest } from '@/shared/api/types';
import { AxiosError } from 'axios';
import { PropsWithChildren, useCallback, useEffect } from 'react';

const ApiErrorBoundary = ({ children }: PropsWithChildren) => {
  const errorHandler = useCallback((error: Error) => {
    if (error instanceof AxiosError) {
      const config = error.config as TRequest;

      if (config?.ignoreAllErrors) {
        throw error;
      }

      if (config.ignoreErrorStatuses?.length) {
        if (config.ignoreErrorStatuses.includes(error.status as number)) {
          throw error;
        }
      }

      const status = error.response?.status || 500;
      window.location.href = `/error/${status}`;

      throw error;
    }
  }, []);

  useEffect(() => {
    const interceptorId = api.interceptors.response.use(
      undefined,
      errorHandler,
    );

    return () => {
      api.interceptors.response.eject(interceptorId);
    };
  }, [errorHandler]);

  return <>{children}</>;
};

export default ApiErrorBoundary;
