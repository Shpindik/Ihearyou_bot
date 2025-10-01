import { UserListDto } from '@/entities/user/list/models/dtos/list.dto.ts';

/**
 * @example
 * {
 *   "items": [
 *     {
 *       "id": 1,
 *       "telegram_id": 123456789,
 *       "username": "ivan_ivanov",
 *       "first_name": "Иван",
 *       "last_name": "Иванов",
 *       "subscription_type": "free", // еще какие типы подписок?
 *       "last_activity": "2024-01-15T10:30:00Z",
 *       "created_at": "2024-01-01T12:00:00Z"
 *     }
 *   ],
 *   "total": 150,
 *   "page": 1,
 *   "limit": 20,
 *   "pages": 8
 * }
 */

export interface IListResponse {
  list: UserListDto;
}
