import { TLabels, TOrder } from '../types/tabs.type';

export const MOrder: TOrder = [
  'ANALYTICS',
  'MATERIALS',
  'ACCESS_RIGHTS',
  'NOTIFICATIONS',
] as const;

export const MLabels: TLabels = {
  ANALYTICS: 'Аналитика',
  MATERIALS: 'Материалы',
  ACCESS_RIGHTS: 'Права доступа',
  NOTIFICATIONS: 'Уведомления',
};
