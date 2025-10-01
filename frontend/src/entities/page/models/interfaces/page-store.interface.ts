import { TPageState } from '@/entities/page/models/types/page-state.type.ts';

export interface IPageStore {
  state: TPageState;
  loading: boolean;
  loadingText: string;

  setState: (state: TPageState) => void;
  setLoading: (loading: boolean, text?: string) => void;
}
