import {categoryTuple, notificationTuple,} from '@/features/notifications/models';
import UIButton from '@/shared/ui/button';
import UIModal from '@/shared/ui/modal';
import {ComponentPropsWithoutRef, FC} from 'react';

interface INotificationForm {
  name: string;
  message: string;
  auto: 'daily' | 'weekly' | 'monthly' | 'disabled';
  category: 'all' | 'inactive';
  telegram_user_id: number | null;
}

interface IModalProps extends ComponentPropsWithoutRef<'div'> {
  open: boolean;
  onClose: () => void;
  onSubmit: () => void;
  loading: boolean;
  form: INotificationForm;
  setForm: (state: Partial<INotificationForm>) => void;
}

const Modal: FC<IModalProps> = ({
  open,
  onClose,
  onSubmit,
  loading,
  form,
  setForm,
  className = '',
}) => {
  return (
    <UIModal
      open={open}
      onClose={onClose}
      title="Новое уведомление"
      className={`w-full max-w-2xl ${className} bg-white`}
      footer={
        <div className="p-8">
          <UIButton
            theme="primary-fill"
            onClick={onSubmit}
            disabled={loading || !form.name.trim() || !form.message.trim()}
            className="w-full"
          >
            {loading ? 'Создание...' : 'Создать'}
          </UIButton>
        </div>
      }
    >
      <div className="p-8 flex flex-col gap-6">
        <div className="flex flex-col gap-6">
          <h2>Название (видно только вам)</h2>

          <textarea
            value={form.name}
            onChange={(e) => setForm({ name: e.target.value })}
            placeholder="Введите название уведомления"
            className="w-full px-3 py-2 border border-ui-gray-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ui-primary"
          />
        </div>

        <div className="flex flex-col gap-6">
          <h2>Текст уведомления (виден пользователям)</h2>

          <textarea
            value={form.message}
            onChange={(e) => setForm({ message: e.target.value })}
            placeholder="Введите текст уведомления"
            rows={3}
            className="w-full px-3 py-2 border border-ui-gray-border rounded-lg focus:outline-none focus:ring-2 focus:ring-ui-primary resize-none"
          />
        </div>

        <div className="flex flex-col gap-6">
          <h2>Авторассылка уведомлений</h2>

          <div className="flex flex-col gap-2">
            {notificationTuple.map((option) => (
              <label
                key={option.value}
                className="flex items-center gap-4 cursor-pointer"
              >
                <input
                  type="radio"
                  name="auto"
                  value={option.value}
                  checked={form.auto === option.value}
                  onChange={(e) => setForm({ auto: e.target.value as any })}
                />
                <p>{option.label}</p>
              </label>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-6">
          <h2>Категория пользователей</h2>

          <div className="flex flex-col gap-2">
            {categoryTuple.map((option) => (
              <label
                key={option.value}
                className="flex items-center gap-4 cursor-pointer"
              >
                <input
                  type="radio"
                  name="category"
                  value={option.value}
                  checked={form.category === option.value}
                  onChange={(e) => setForm({ category: e.target.value as any })}
                />
                <p>{option.label}</p>
              </label>
            ))}
          </div>
        </div>
      </div>
    </UIModal>
  );
};

export default Modal;
