import {create} from 'zustand';

interface INotificationForm {
  name: string;
  message: string;
  auto: 'daily' | 'weekly' | 'monthly' | 'disabled';
  category: 'all' | 'inactive';
  telegram_user_id: number;
}

interface INotificationActionsStore {
  form: INotificationForm;

  set: (state: Partial<INotificationForm>) => void;
  clear: () => void;
}

const initForm = (): INotificationForm => ({
  name: '',
  message: '',
  auto: 'disabled',
  category: 'all',
  telegram_user_id: 0,
});

export const useNotificationActionsStore = create<INotificationActionsStore>(
  (set, get) => ({
    form: initForm(),

    set: (state: Partial<INotificationForm>) =>
      set({ form: { ...get().form, ...state } }),

    clear: (): void => set({ form: initForm() }),
  }),
);
