/**
 * @example
 * {
 *   "id": 123,
 *   "telegram_user_id": 123456789,
 *   "menu_item_id": 1,
 *   "activity_type": "view",
 *   "rating": null,
 *   "search_query": "слуховые аппараты"
 * }
 */

export interface IActivityResponse {
  id: number;
  telegram_user_id: number;
  menu_item_id: number;
  activity_type: string;
  rating: number;
  search_query: string;
}
