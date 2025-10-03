/**
 * @example
 * {
 *   "id": 1,
 *   "telegram_id": 123456789,
 *   "username": "ivan_ivanov",
 *   "first_name": "Иван",
 *   "last_name": "Иванов",
 *   "subscription_type": "free",
 *   "last_activity": "2024-01-15T10:30:00Z",
 *   "reminder_sent_at": "2024-01-10T09:00:00Z",
 *   "created_at": "2024-01-01T12:00:00Z",
 *   "activities_count": 25,
 *   "questions_count": 3
 * }
 */

export interface IUserDetailsResponse {
  id: number;
  telegram_id: number;
  username: string;
  first_name: string;
  last_name: string;
  subscription_type: string;
  last_activity: string;
  reminder_sent_at: string;
  created_at: string;
  activities_count: number;
  questions_count: number;
}
