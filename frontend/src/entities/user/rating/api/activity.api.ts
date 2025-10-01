import { IRatingRequest, IRatingResponse } from '@/entities/user/rating';
import { api } from '@/shared/api';
import { IError } from '@/shared/models/interfaces/error.interface.ts';

export const rateInformation = async (body: IRatingRequest) => {
  return api
    .post<IRatingResponse | IError>('/api/v1/ratings', body, {
      baseURL: import.meta.env.VITE_API_URL,
    })
    .then((response) => response.data)
    .catch((e) => console.log(e));
};
