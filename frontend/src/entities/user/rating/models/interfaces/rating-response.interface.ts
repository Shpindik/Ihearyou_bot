/**
 * @example
 * {
 *   "id": 789,
 *   "telegram_user_id": 123456789,
 *   "menu_item_id": 1,
 *   "activity_type": "rating",
 *   "rating": 5,
 *   "search_query": null
 * }
 */

export interface IRatingResponse {
  id: number;
  telegram_user_id: number;
  menu_item_id: number;
  activity_type: string;
  rating: number;
  search_query: number;
}
