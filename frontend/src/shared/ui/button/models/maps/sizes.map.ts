import { TSizes } from '../types';

export const MSizes: Record<TSizes, string> = {
  S: 'h-8 min-h-8 px-3 text-r-sm rounded-2xl',
  M: 'h-10 min-h-10 px-4 text-r-base rounded-2xl',
  L: 'h-12 min-h-12 px-6 text-r-lg rounded-2xl',
  XL: 'h-16 min-h-16 px-8 text-r-xl rounded-2xl',
  none: '',
  'S-I': 'h-8 w-8 min-h-8 min-w-8 text-r-sm rounded-full',
  'M-I': 'h-10 w-10 min-h-10 min-w-10 text-r-base rounded-full',
  'L-I': 'h-12 w-12 min-h-12 min-w-12 text-r-lg rounded-full',
};
