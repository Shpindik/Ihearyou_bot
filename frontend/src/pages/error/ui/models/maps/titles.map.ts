import { EErrors } from '@/pages/error/ui/models/enums';

export const MTitles: Record<EErrors, string> = {
  [EErrors.NOT_AUTHORIZED]: 'Вы не авторизованы',
  [EErrors.NOT_FOUND]: 'Страница не найдена',
  [EErrors.INTERNAL_SERVER_ERROR]: 'Внутренняя ошибка сервера',
};
