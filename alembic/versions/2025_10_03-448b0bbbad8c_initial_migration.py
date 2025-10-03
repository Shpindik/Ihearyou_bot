"""Initial migration

Revision ID: 448b0bbbad8c
Revises: 
Create Date: 2025-10-03 14:55:56.333245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '448b0bbbad8c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создание всех таблиц."""
    # Создание таблицы администраторов
    op.create_table('admin_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, comment='Email администратора (логин + уведомления)'),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_users_id'), 'admin_users', ['id'], unique=False)
    op.create_index('ix_admin_users_email', 'admin_users', ['email'], unique=True)
    op.create_index('ix_admin_users_is_active', 'admin_users', ['is_active'], unique=False)
    op.create_index('ix_admin_users_role', 'admin_users', ['role'], unique=False)
    op.create_index('ix_admin_users_username', 'admin_users', ['username'], unique=True)

    # Создание таблицы пользователей Telegram
    op.create_table('telegram_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('subscription_type', sa.String(length=20), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reminder_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('activities_count', sa.Integer(), nullable=False),
        sa.Column('questions_count', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telegram_users_id'), 'telegram_users', ['id'], unique=False)
    op.create_index('ix_telegram_users_subscription_type', 'telegram_users', ['subscription_type'], unique=False)
    op.create_index('ix_telegram_users_telegram_id', 'telegram_users', ['telegram_id'], unique=True)
    op.create_index('ix_telegram_users_inactive_reminder', 'telegram_users', ['last_activity', 'reminder_sent_at'], unique=False)
    op.create_index('ix_telegram_users_last_activity', 'telegram_users', ['last_activity'], unique=False)
    op.create_index('ix_telegram_users_reminder_sent_at', 'telegram_users', ['reminder_sent_at'], unique=False)

    # Создание таблицы пунктов меню
    op.create_table('menu_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('item_type', sa.String(length=20), nullable=False, comment='Тип: navigation (имеет children) или content (имеет content)'),
        sa.Column('bot_message', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('access_level', sa.String(length=20), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False),
        sa.Column('download_count', sa.Integer(), nullable=False),
        sa.Column('rating_sum', sa.Integer(), nullable=False),
        sa.Column('rating_count', sa.Integer(), nullable=False),
        sa.Column('average_rating', sa.DECIMAL(precision=3, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['menu_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_menu_items_id'), 'menu_items', ['id'], unique=False)
    op.create_index('ix_menu_items_access_level', 'menu_items', ['access_level'], unique=False)
    op.create_index('ix_menu_items_active_parent', 'menu_items', ['is_active', 'parent_id'], unique=False)
    op.create_index('ix_menu_items_is_active', 'menu_items', ['is_active'], unique=False)
    op.create_index('ix_menu_items_item_type', 'menu_items', ['item_type'], unique=False)
    op.create_index('ix_menu_items_parent_id', 'menu_items', ['parent_id'], unique=False)
    op.create_index('ix_menu_items_type_active', 'menu_items', ['item_type', 'is_active'], unique=False)

    # Создание таблицы файлов контента
    op.create_table('content_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('menu_item_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('telegram_file_id', sa.String(length=255), nullable=True, comment='File ID от Telegram для переиспользования медиафайлов'),
        sa.Column('caption', sa.Text(), nullable=True, comment='Подпись к медиафайлу (для фото, видео и т.д.)'),
        sa.Column('text_content', sa.Text(), nullable=True, comment='Текстовый контент для типа TEXT'),
        sa.Column('external_url', sa.Text(), nullable=True, comment='URL для внешних ресурсов (YouTube, VK, Web App, etc)'),
        sa.Column('web_app_short_name', sa.String(length=255), nullable=True, comment='Короткое имя Web App (для type=WEB_APP)'),
        sa.Column('local_file_path', sa.Text(), nullable=True, comment='Путь к локальному файлу ДО загрузки в Telegram'),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True, comment='Ширина изображения/видео'),
        sa.Column('height', sa.Integer(), nullable=True, comment='Высота изображения/видео'),
        sa.Column('duration', sa.Integer(), nullable=True, comment='Длительность видео/аудио в секундах'),
        sa.Column('thumbnail_telegram_file_id', sa.String(length=255), nullable=True, comment='File ID превью от Telegram'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_files_id'), 'content_files', ['id'], unique=False)
    op.create_index('ix_content_files_content_type', 'content_files', ['content_type'], unique=False)
    op.create_index('ix_content_files_external_url', 'content_files', ['external_url'], unique=False)
    op.create_index('ix_content_files_menu_item_id', 'content_files', ['menu_item_id'], unique=True)
    op.create_index('ix_content_files_telegram_file_id', 'content_files', ['telegram_file_id'], unique=False)
    op.create_index('ix_content_files_web_app_short_name', 'content_files', ['web_app_short_name'], unique=False)

    # Создание таблицы активности пользователей
    op.create_table('user_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('menu_item_id', sa.Integer(), nullable=True),
        sa.Column('search_query', sa.Text(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ),
        sa.ForeignKeyConstraint(['telegram_user_id'], ['telegram_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_activities_id'), 'user_activities', ['id'], unique=False)
    op.create_index('ix_user_activities_activity_type', 'user_activities', ['activity_type'], unique=False)
    op.create_index('ix_user_activities_created_at', 'user_activities', ['created_at'], unique=False)
    op.create_index('ix_user_activities_menu_item_id', 'user_activities', ['menu_item_id'], unique=False)
    op.create_index('ix_user_activities_telegram_user_id', 'user_activities', ['telegram_user_id'], unique=False)

    # Создание таблицы шаблонов сообщений
    op.create_table('message_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_templates_id'), 'message_templates', ['id'], unique=False)
    op.create_index('ix_message_templates_is_active', 'message_templates', ['is_active'], unique=False)

    # Создание таблицы уведомлений
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['message_templates.id'], ),
        sa.ForeignKeyConstraint(['telegram_user_id'], ['telegram_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'], unique=False)
    op.create_index('ix_notifications_sent_at', 'notifications', ['sent_at'], unique=False)
    op.create_index('ix_notifications_status', 'notifications', ['status'], unique=False)
    op.create_index('ix_notifications_telegram_user_id', 'notifications', ['telegram_user_id'], unique=False)
    op.create_index('ix_notifications_template_id', 'notifications', ['template_id'], unique=False)

    # Создание таблицы вопросов пользователей
    op.create_table('user_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('answer_text', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['telegram_user_id'], ['telegram_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_questions_id'), 'user_questions', ['id'], unique=False)
    op.create_index('ix_user_questions_admin_user_id', 'user_questions', ['admin_user_id'], unique=False)
    op.create_index('ix_user_questions_answered_at', 'user_questions', ['answered_at'], unique=False)
    op.create_index('ix_user_questions_created_at', 'user_questions', ['created_at'], unique=False)
    op.create_index('ix_user_questions_status', 'user_questions', ['status'], unique=False)
    op.create_index('ix_user_questions_telegram_user_id', 'user_questions', ['telegram_user_id'], unique=False)


def downgrade() -> None:
    """Удаление всех таблиц."""
    # Удаляем таблицы в обратном порядке от зависимостей
    op.drop_table('user_questions')
    op.drop_table('notifications')
    op.drop_table('message_templates')
    op.drop_table('user_activities')
    op.drop_table('content_files')
    op.drop_table('menu_items')
    op.drop_table('telegram_users')
    op.drop_table('admin_users')
