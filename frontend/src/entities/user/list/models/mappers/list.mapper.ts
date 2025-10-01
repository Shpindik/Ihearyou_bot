import { UserItemDto } from '../dtos';
import { IListResponse } from '../interfaces';

export const userItemMapper = (dto: UserItemDto) => ({
  id: dto.id,
  telegramId: dto.telegram_id,
  username: dto.username,
  firstName: dto.first_name,
  lastName: dto.last_name,
  subscriptionType: dto.subscription_type,
  lastActivity: dto.last_activity,
  createdAt: dto.created_at,
});

export const userListMapper = (response: IListResponse) => {
  if (!response || (response && 'error' in response)) return [];

  return response.list.items.map(userItemMapper);
};
