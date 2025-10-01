import { NotificationItemDto, NotificationsListDto } from '../dtos';
import { INotificationListResponse } from '../interfaces';

export const notificationItemMapper = (dto: NotificationItemDto) => ({
  id: dto.id,
  telegramUserId: dto.telegram_user_id,
  message: dto.message,
  status: dto.status,
  createdAt: dto.created_at,
  sentAt: dto.sent_at,
  templateId: dto.template_id,
});

export const notificationListMapper = (
  response: INotificationListResponse | { list: NotificationsListDto },
) => {
  if (!response?.list?.items) return { items: [], total: 0 };

  return {
    items: response.list.items.map(notificationItemMapper),
    total: response.list.total,
  };
};
