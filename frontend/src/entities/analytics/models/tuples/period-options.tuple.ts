import { PeriodType } from '../types';

type PeriodOptionValue = PeriodType | '';

type PeriodOption = {
  readonly value: PeriodOptionValue;
  readonly label: string;
};

export const PERIOD_OPTIONS: readonly PeriodOption[] = [
  { value: '', label: 'Все время' },
  { value: 'day', label: 'Сегодня' },
  { value: 'week', label: 'За неделю' },
  { value: 'month', label: 'За месяц' },
  { value: 'year', label: 'За год' },
] as const;

export type PeriodOptionType = (typeof PERIOD_OPTIONS)[number];
