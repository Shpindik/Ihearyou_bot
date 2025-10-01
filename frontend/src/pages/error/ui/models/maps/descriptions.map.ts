import { EErrors } from '@/pages/error/ui/models/enums';

export const MDescriptions: Record<EErrors, string> = {
  [EErrors.NOT_AUTHORIZED]: 'Для авторизации перезагрузите страницу.',
  [EErrors.NOT_FOUND]:
    'Убедитесь, что адрес страницы введён правильно, или начните с главной страницы.',
  [EErrors.INTERNAL_SERVER_ERROR]:
    'Произошла внутренняя ошибка сервера. Попробуйте перезагрузить страницу.',
};
