import {
  IToken,
  ITokenRefreshRequest,
  ITokenResponse,
  tokenMapper,
} from '@/entities/user';
import { api } from '@/shared/api';

export const login = async (token: string): Promise<IToken> => {
  return api
    .post<ITokenResponse>(
      '/admin/auth/login',
      {
        token,
      },
      {
        baseURL: import.meta.env.SERVICE_AUTH_API,
      },
    )
    .then((response) => response.data)
    .then(tokenMapper);
};

export const refresh = async (data: ITokenRefreshRequest): Promise<IToken> => {
  return api
    .post<ITokenResponse>('/admin/auth/refresh', data, {
      baseURL: import.meta.env.SERVICE_AUTH_API,
    })
    .then((response) => response.data)
    .then(tokenMapper);
};
