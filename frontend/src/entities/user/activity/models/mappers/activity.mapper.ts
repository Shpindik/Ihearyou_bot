import { ActivityResponseDto } from '../dtos';

export const activityMapper = (dto: ActivityResponseDto) => ({
  id: dto.id,
  telegramUserId: dto.telegram_user_id,
  menuItemId: dto.menu_item_id,
  activityType: dto.activity_type,
  rating: dto.rating,
  searchQuery: dto.search_query,
});
