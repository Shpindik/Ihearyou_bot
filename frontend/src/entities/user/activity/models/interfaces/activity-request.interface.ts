/**
 * @example
 * {
 *   "telegram_user_id": 123456789,
 *   "menu_item_id": 1,
 *   "activity_type": "view",
 *   "search_query": "слуховые аппараты"
 * }
 */

export interface IActivityRequest {
  telegram_user_id: number;
  menu_item_id: number;
  activity_type: string;
  search_query: string;
}
