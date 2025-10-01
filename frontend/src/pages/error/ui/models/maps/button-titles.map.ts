import { EErrors } from '@/pages/error/ui/models';

export const MButtonTitles: Record<EErrors, string> = {
  [EErrors.NOT_AUTHORIZED]: 'Перезагрузите страницу',
  [EErrors.NOT_FOUND]: 'На главную страницу',
  [EErrors.INTERNAL_SERVER_ERROR]: 'Перезагрузите страницу',
};
