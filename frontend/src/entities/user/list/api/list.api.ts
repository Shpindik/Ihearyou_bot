import { IListItem } from '@/entities/user/list';
import { IListRequest } from '@/entities/user/list/models/interfaces/list-request.interface.ts';
import { api } from '@/shared/api';
import { IError } from '@/shared/models/interfaces/error.interface.ts';
import { convertQuery } from '@/shared/utils';

export const getUserList = async (
  body: IListRequest,
): Promise<IListItem[] | IError> => {
  const query = convertQuery(body);

  return api
    .get(`/admin/telegram-users/${query}`, {
      baseURL: import.meta.env.VITE_API_URL,
    })
    .then((response) => response.data)
    .catch((e) => console.log(e));
};
