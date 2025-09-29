import {
  type AxiosError,
  type AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios';
import { getItem } from '@/shared/utils';
import { TRequest } from '@/shared/api/types';
import { IToken, TOKEN_STORE_KEY } from '@/entities/user';

export interface ConsoleError {
  status: number;
  data: unknown;
}

export const requestInterceptor = (
  config: InternalAxiosRequestConfig,
): InternalAxiosRequestConfig => {
  const { state } =
    getItem<{ state: { token: IToken | null } }>(TOKEN_STORE_KEY) || {};

  if (state?.token?.access) {
    config.headers?.set('X-Token', state.token.access);
  }

  if ((config as TRequest).ignoreXHeaders) {
    config.headers?.set('X-Token', undefined);
    config.headers?.set('X-App-Version', undefined);
    config.headers?.set('X-App-Type', undefined);
  }

  return config;
};

export const successInterceptor = (response: AxiosResponse): AxiosResponse => {
  return response;
};

export const errorInterceptor = async (error: AxiosError): Promise<void> => {
  if (error.response?.status === 401) {
    await Promise.reject(error);
  } else {
    if (error.response) {
      const errorMessage: ConsoleError = {
        status: error.response.status,
        data: error.response.data,
      };
      console.error(errorMessage);
    } else if (error.request) {
      console.error(error.request);
    } else {
      console.error('Error', error.message);
    }
    await Promise.reject(error);
  }
};
