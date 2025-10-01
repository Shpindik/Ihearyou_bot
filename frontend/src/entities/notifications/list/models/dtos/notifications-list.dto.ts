import {NotificationItemDto} from './notification-item.dto';

export interface NotificationsListDto {
  items: NotificationItemDto[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}
