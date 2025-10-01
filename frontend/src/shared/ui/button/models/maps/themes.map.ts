import { TThemes } from '../types';

export const MThemes: Record<TThemes, string> = {
  'primary-fill':
    'bg-ui-purple-primary text-white fine:hover:bg-ui-purple-primary/90',
  'primary-outline':
    'border border-ui-purple-primary text-ui-purple-primary hover:bg-ui-purple-primary/5',
  'secondary-fill':
    'bg-secondary text-ui-purple-primary fine:hover:bg-secondaryHover',
  'secondary-outline':
    'text-ui-purple-primary border border-secondary hover:bg-secondaryHover/5',
  'success-fill':
    'bg-ui-green-success text-white fine:hover:bg-ui-green-success/90',
  'success-outline':
    'border border-ui-green-success text-ui-green-success hover:bg-ui-green-success/5',
  'error-fill': 'bg-ui-red-error text-white fine:hover:bg-ui-red-error/90',
  'error-outline':
    'border border-ui-red-error text-ui-red-error hover:bg-ui-red-error/5',
  'warning-fill':
    'bg-ui-orange-warning text-white fine:hover:bg-ui-orange-warning/90',
  'warning-outline':
    'border border-ui-orange-warning text-ui-orange-warning fine:hover:bg-ui-orange-warning/5',
  'info-fill': 'bg-ui-blue-info text-white fine:hover:bg-ui-blue-info/90',
  'info-outline':
    'border border-ui-blue-info text-ui-blue-info hover:bg-ui-blue-info/5',
  'grey-fill':
    'bg-ui-gray-bg-block text-ui-gray-text-main fine:hover:bg-slavHover',
  'grey-outline':
    'border border-ui-gray-border-main text-ui-gray-text-secondary focus:text-ui-gray-text-main',
  'black-fill':
    'bg-ui-gray-text-main text-white fine:hover:bg-ui-gray-text-main/90',
  'black-outline':
    'border border-ui-gray-text-main text-ui-gray-text-secondary',
  none: '',
};
