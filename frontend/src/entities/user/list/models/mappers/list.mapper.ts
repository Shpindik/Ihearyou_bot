import {UserItemDto, UserListDto} from '../dtos';
import {IListResponse} from '../interfaces';

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

export const userListMapper = (
  response: IListResponse | { list: UserListDto },
) => {
  if (!response?.list?.items) return { items: [], total: 0 };

  return {
    items: response.list.items.map(userItemMapper),
    total: response.list.total,
  };
};
