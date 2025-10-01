export interface IListItem {
  id: number;
  telegram_id: number;
  username: string;
  first_name: string;
  last_name: string;
  subscription_type: string; // еще какие?
  last_activity: string;
  created_at: string;
}
