import { TUserItem, userListMapper } from '@/entities/user/list';
import { IListRequest } from '@/entities/user/list/models/interfaces/list-request.interface.ts';
import { IListResponse } from '@/entities/user/list/models/interfaces/list-response.interface.ts';
import { api } from '@/shared/api';
import { convertQuery } from '@/shared/utils';

export const getAdminList = async (
  body: IListRequest,
): Promise<{ items: TUserItem[]; total: number }> => {
  const query = convertQuery(body);

  return api
    .get<IListResponse>(`/v1/admin/telegram-users${query}`)
    .then((response) => {
      return response.data;
    })
    .then(userListMapper)
    .catch((e) => {
      console.log(e);
      throw e;
    });
};
