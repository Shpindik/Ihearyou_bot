import { NotificationsListDto } from '@/entities/notifications/list/models/dtos';

export const notificationsListMock: NotificationsListDto = {
  items: [
    {
      id: 1,
      telegram_user_id: 123456789,
      message: 'Напоминание: не забудьте проверить новые материалы!',
      status: 'sent',
      created_at: '2024-01-15T20:00:00Z',
      sent_at: '2024-01-15T20:00:00Z',
      template_id: 1,
    },
    {
      id: 2,
      telegram_user_id: 987654321,
      message: 'Добро пожаловать в наш бот!',
      status: 'sent',
      created_at: '2024-01-14T15:30:00Z',
      sent_at: '2024-01-14T15:30:00Z',
      template_id: 2,
    },
    {
      id: 3,
      telegram_user_id: 456789123,
      message: 'У вас есть новые ответы на вопросы',
      status: 'pending',
      created_at: '2024-01-13T10:15:00Z',
      sent_at: null,
      template_id: null,
    },
  ],
  total: 50,
  page: 1,
  limit: 20,
  pages: 3,
};
