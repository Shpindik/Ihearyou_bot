import { TNotificationItem } from '@/entities/notifications';
import { api } from '@/shared/api';

export const sendNotification = async (data: {
  telegram_user_id: number;
  message: string;
}): Promise<TNotificationItem> => {
  return api
    .post('/v1/admin/notifications', data)
    .then((response) => response.data);
};

export const getNotification = async (
  id: number,
): Promise<TNotificationItem> => {
  return api
    .get(`/v1/admin/notifications/${id}`)
    .then((response) => response.data);
};

export const updateNotification = async (
  id: number,
  data: {
    status?: string;
    sent_at?: string;
  },
): Promise<TNotificationItem> => {
  return api
    .put(`/v1/admin/notifications/${id}`, data)
    .then((response) => response.data);
};

export const deleteNotification = async (id: number): Promise<void> => {
  return api.delete(`/v1/admin/notifications/${id}`).then(() => {});
};
