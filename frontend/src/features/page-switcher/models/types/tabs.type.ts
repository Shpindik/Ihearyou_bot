import { TPageState } from '@/entities/page';

export type TOrder = readonly [
  'ANALYTICS',
  'MATERIALS',
  'USERS_LIST',
  'NOTIFICATIONS',
];

export type TLabels = Record<TPageState, string>;
