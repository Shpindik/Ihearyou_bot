import { IPageStore, TPageState } from '@/entities/page/models';
import { create } from 'zustand';

export const usePageStore = create<IPageStore>((set) => ({
  state: 'ANALYTICS',
  loading: false,
  loadingText: '',

  setState: (state: TPageState) => set({ state }),
  setLoading: (loading: boolean, text = '') =>
    set({ loading, loadingText: text }),
}));
