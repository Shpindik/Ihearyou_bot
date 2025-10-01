import {
  IToken,
  ITokenRefreshRequest,
  ITokenResponse,
  tokenMapper,
} from '@/entities/admin';
import { api } from '@/shared/api';
import { TRequest } from '@/shared/api/types';

export const login = async (
  username: string,
  password: string,
): Promise<IToken> => {
  const config: TRequest = {
    baseURL: import.meta.env.SERVICE_AUTH_API,
    ignoreAllErrors: true,
  };

  return api
    .post<ITokenResponse>(
      '/api/v1/admin/auth/login',
      {
        username,
        password,
      },
      config,
    )
    .then((response) => response.data)
    .then(tokenMapper);
};

export const refresh = async (data: ITokenRefreshRequest): Promise<IToken> => {
  const config: TRequest = {
    baseURL: import.meta.env.SERVICE_AUTH_API,
    ignoreAllErrors: true,
  };

  return api
    .post<ITokenResponse>('/api/v1/admin/auth/refresh', data, config)
    .then((response) => response.data)
    .then(tokenMapper);
};
