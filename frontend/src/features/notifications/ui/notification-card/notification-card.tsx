import {TNotificationItem} from '@/entities/notifications/list/types/notification-item.type';
import CloseIcon from '@/shared/svg/close.icon';
import UIBlock from '@/shared/ui/block/ui-block';
import UIFullBackdropLoader from '@/shared/ui/full-backdrop-loader';
import {ComponentPropsWithoutRef, FC, MouseEvent} from 'react';

interface IProps extends ComponentPropsWithoutRef<'div'> {
  notification: TNotificationItem;
  onDelete: (id: number) => void;
  isDeleting?: boolean;
}

const NotificationCard: FC<IProps> = ({
  notification,
  onDelete,
  isDeleting = false,
  className = '',
  ...props
}) => {
  const handleDelete = (e: MouseEvent): void => {
    e.stopPropagation();
    onDelete(notification.id);
  };

  return (
    <UIBlock
      className={`relative p-8 min-h-[200px] ${className}`}
      background="bg-ui-purple-secondary"
      {...props}
    >
      <button
        onClick={handleDelete}
        className="absolute top-3 right-3 p-1 transition-colors"
        aria-label="Удалить уведомление"
        disabled={isDeleting}
      >
        <CloseIcon />
      </button>

      <div className="flex flex-col gap-8">
        <h3>{notification.message}</h3>
        <p>
          Статус:{' '}
          {notification.status === 'sent'
            ? 'Отправлено'
            : notification.status === 'pending'
              ? 'Ожидает отправки'
              : 'Ошибка отправки'}
        </p>
      </div>

      <UIFullBackdropLoader
        loading={isDeleting}
        text="Удаление..."
        background={true}
        className="absolute inset-0 z-10 rounded-2xl"
      />
    </UIBlock>
  );
};

export default NotificationCard;
