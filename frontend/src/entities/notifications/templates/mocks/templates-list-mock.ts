import { TemplatesListDto } from '@/entities/notifications/templates/models/dtos';

export const templatesListMock: TemplatesListDto = {
  items: [
    {
      id: 1,
      name: 'Еженедельное напоминание',
      message_template:
        'Привет! У нас есть новые материалы, которые могут быть полезны для вас.',
      is_active: true,
      created_at: '2024-01-01T12:00:00Z',
      updated_at: '2024-01-01T12:00:00Z',
    },
    {
      id: 2,
      name: 'Добро пожаловать',
      message_template: 'Добро пожаловать в наш бот! Мы рады помочь вам.',
      is_active: true,
      created_at: '2024-01-02T10:00:00Z',
      updated_at: '2024-01-02T10:00:00Z',
    },
    {
      id: 3,
      name: 'Новые ответы',
      message_template: 'У вас есть новые ответы на ваши вопросы.',
      is_active: false,
      created_at: '2024-01-03T14:30:00Z',
      updated_at: '2024-01-10T16:45:00Z',
    },
  ],
};
