import {AxiosRequestConfig} from 'axios';

export type TRequest = AxiosRequestConfig & {
  ignoreXHeaders?: boolean;
  ignoreErrorStatuses?: number[];
  ignoreAllErrors?: boolean;
};
