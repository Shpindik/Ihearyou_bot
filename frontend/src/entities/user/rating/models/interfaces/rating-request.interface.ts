/**
 * @example
 * {
 *   "telegram_user_id": 123456789,
 *   "menu_item_id": 1,
 *   "rating": 5
 * }
 */

export interface IRatingRequest {
  telegram_user_id: number;
  menu_item_id: number;
  rating: number;
}
