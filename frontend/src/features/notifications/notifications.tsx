import {
  deleteNotification,
  sendNotification,
} from '@/entities/notifications/actions/api/notification-actions.api';
import { useNotificationActionsStore } from '@/entities/notifications/actions/store';
import { getNotificationsList } from '@/entities/notifications/list/api/notifications-list.api';
import { TNotificationItem } from '@/entities/notifications/list/types/notification-item.type';
import UIFullBackdropLoader from '@/shared/ui/full-backdrop-loader';
import { ComponentPropsWithoutRef, FC, useEffect, useState } from 'react';
import { CreateNotificationCard, NotificationCard } from './ui';
import Modal from './ui/create-notification/modal/modal';

export const Notifications: FC<ComponentPropsWithoutRef<'div'>> = ({
  className,
}) => {
  const { form, set, clear } = useNotificationActionsStore();

  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [card, setCard] = useState<number | null>(null);
  const [notifications, setNotifications] = useState<TNotificationItem[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    getNotificationsList({})
      .then((response) => {
        setNotifications(response.items);
        setInitialLoading(false);
      })
      .catch((error) => {
        console.error('Ошибка при загрузке уведомлений:', error);
        setInitialLoading(false);
      });
  }, []);

  const handleDelete = (id: number) => {
    if (window.confirm('Вы уверены, что хотите удалить это уведомление?')) {
      setCard(id);
      deleteNotification(id)
        .then(() => {
          setNotifications((prev) => prev.filter((n) => n.id !== id));
          setCard(null);
        })
        .catch((error) => {
          console.error('Ошибка при удалении уведомления:', error);
          setCard(null);
        });
    }
  };

  const handleCreate = () => {
    if (!form.message.trim()) return;

    setLoading(true);

    sendNotification({
      telegram_user_id: form.telegram_user_id,
      message: form.message,
    })
      .then((newNotification) => {
        setNotifications((prev) => [newNotification, ...prev]);
        setIsModalOpen(false);
        setLoading(false);
        clear();
      })
      .catch((error) => {
        console.error('Ошибка при создании уведомления:', error);
        setLoading(false);
      });
  };

  const handleOpenModal = () => {
    clear();
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div className={className}>
      <div className="p-4">
        <div className="flex items-center justify-between mb-6">
          <h1>Уведомления</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-[24px]">
          <CreateNotificationCard onClick={handleOpenModal} />

          {notifications.map((notification) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onDelete={handleDelete}
              isDeleting={card === notification.id}
            />
          ))}
        </div>
      </div>

      <UIFullBackdropLoader
        loading={initialLoading}
        text="Загрузка уведомлений..."
        background={true}
      />

      <Modal
        open={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleCreate}
        loading={loading}
        form={form}
        setForm={() => set}
      />
    </div>
  );
};

export default Notifications;
