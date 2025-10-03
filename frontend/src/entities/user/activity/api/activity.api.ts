import {IActivityRequest} from '@/entities/user/activity/models';
import {IActivityResponse} from '@/entities/user/activity/models/interfaces/activity-response.interface.ts';
import {api} from '@/shared/api';
import {IError} from '@/shared/models/interfaces/error.interface.ts';

export const createActivity = async (body: IActivityRequest) => {
  return api
    .post<IActivityResponse | IError>('/v1/user-activities', body, {
      baseURL: import.meta.env.VITE_API_URL,
    })
    .then((response) => response.data)
    .catch((e) => console.log(e));
};
