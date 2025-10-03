import {create, StateCreator} from 'zustand';
import {createJSONStorage, devtools, persist} from 'zustand/middleware';
import {ITokenRefreshRequest, ITokenStore, login, refresh, TOKEN_STORE_KEY,} from '@/entities/admin';
import {logger} from '@/shared/utils';

const middlewares = (f: StateCreator<ITokenStore>) =>
  devtools(
    persist(logger(f), {
      name: TOKEN_STORE_KEY,
      storage: createJSONStorage(() => localStorage),
    }),
  );

const storeCreator = middlewares((set, get) => ({
  logged: false,
  token: null,

  login: async (username: string, password: string): Promise<void> =>
    login(username, password)
      .then((token) => set({ token, logged: true }))
      .catch((e) => {
        get().logout();
        return Promise.reject(e.response?.data ?? { error: e.message });
      }),

  refresh: async (request: ITokenRefreshRequest): Promise<void> =>
    refresh(request)
      .then((token) => set({ token, logged: true }))
      .catch((e) => {
        get().logout();
        return Promise.reject(e.response?.data ?? { error: e.message });
      }),

  logout: () => set({ logged: false, token: null }),
}));

export const useTokenStore = create(storeCreator);
