import {TLabels, TOrder} from '../types/tabs.type';

export const MOrder: TOrder = [
  'ANALYTICS',
  'MATERIALS',
  'USERS_LIST',
  'NOTIFICATIONS',
] as const;

export const MLabels: TLabels = {
  ANALYTICS: 'Аналитика',
  MATERIALS: 'Материалы',
  USERS_LIST: 'Список пользователей',
  NOTIFICATIONS: 'Уведомления',
};
