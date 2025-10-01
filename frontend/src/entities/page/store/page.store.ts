import { IPageStore, TPageState } from '@/entities/page/models';
import { create } from 'zustand';

export const usePageStore = create<IPageStore>((set) => ({
  state: 'ANALYTICS',

  setState: (state: TPageState) => set({ state }),
}));
