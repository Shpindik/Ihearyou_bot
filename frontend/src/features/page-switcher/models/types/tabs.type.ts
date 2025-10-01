import { TPageState } from '@/entities/page';

export type TOrder = readonly [
  'ANALYTICS',
  'MATERIALS',
  'ACCESS_RIGHTS',
  'NOTIFICATIONS',
];

export type TLabels = Record<TPageState, string>;
