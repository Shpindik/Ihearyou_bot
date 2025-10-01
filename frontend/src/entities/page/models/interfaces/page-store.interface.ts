import { TPageState } from '@/entities/page/models/types/page-state.type.ts';

export interface IPageStore {
  state: TPageState;

  setState: (state: TPageState) => void;
}
