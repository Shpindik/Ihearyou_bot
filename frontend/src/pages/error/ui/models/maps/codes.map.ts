import { EErrors } from '@/pages/error/ui/models/enums';

export const MCodes: Record<EErrors, string> = {
  [EErrors.NOT_AUTHORIZED]: '401',
  [EErrors.NOT_FOUND]: '404',
};
