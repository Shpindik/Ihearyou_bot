export interface NotificationItemDto {
  id: number;
  telegram_user_id: number;
  message: string;
  status: 'pending' | 'sent' | 'failed';
  created_at: string;
  sent_at: string | null;
  template_id: number | null;
}
