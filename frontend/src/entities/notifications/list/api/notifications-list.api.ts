import {
  INotificationListRequest,
  INotificationListResponse,
  TNotificationItem,
  notificationListMapper,
  notificationsListMock,
} from '@/entities/notifications';
import { api } from '@/shared/api';
import { convertQuery } from '@/shared/utils';

export const getNotificationsList = async (
  body: INotificationListRequest,
): Promise<{ items: TNotificationItem[]; total: number }> => {
  const query = convertQuery(body);

  return api
    .get<INotificationListResponse>(`/v1/admin/notifications${query}`)
    .then((response) => {
      return response.data;
    })
    .then(notificationListMapper)
    .catch((e) => {
      console.log(e);
      return notificationListMapper({ list: notificationsListMock });
    });
};
