/**
 * @example
 * {
 *   "period": "week",
 *   "start_date": "2024-01-01",
 *   "end_date": "2024-01-31"
 * }
 */

export interface IAnalyticsRequest {
  period?: 'day' | 'week' | 'month' | 'year';
  start_date?: string;
  end_date?: string;
}
