import {
  IUserDetailsRequest,
  userDetailsMapper,
} from '@/entities/user/details';
import { IUserDetailsResponse } from '@/entities/user/details/models/interfaces/user-details-response.interface';
import { api } from '@/shared/api';
import { IError } from '@/shared/models/interfaces/error.interface';

export const getUserDetails = async (
  params: IUserDetailsRequest,
): Promise<IUserDetailsResponse | IError> => {
  return api
    .get(`/admin/telegram-users/${params.id}`, {
      baseURL: import.meta.env.VITE_API_URL,
    })
    .then((response) => response.data)
    .then(userDetailsMapper)
    .catch((e) => console.log(e));
};
