# API Schema для Telegram-бота "Я тебя слышу"




## MVP API Design




### Принципы для MVP




1. **Минимальный набор эндпоинтов** - только критичные для работы бота
2. **Простая структура** - без сложных фильтров и сортировок
3. **Базовые CRUD операции** - создание, чтение, обновление, удаление
4. **Стандартные HTTP статус-коды** - 200, 201, 204, 400, 403, 404, 500
5. **Консистентные форматы ответов** - все списки возвращают объекты с полем `items`
6. **Фокус на основной функциональности** - меню, контент, пользователи




## Структура API




### 1. Webhook эндпоинты




#### POST /webhook/telegram




Получение webhook от Telegram для обработки сообщений пользователей.




**Заголовки:**
```
Content-Type: application/json
```
USER
**Тело запроса:**
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "Иван",
      "last_name": "Иванов",
      "username": "ivan_ivanov",
      "language_code": "ru"
    },
    "chat": {
      "id": 123456789,
      "first_name": "Иван",
      "last_name": "Иванов",
      "username": "ivan_ivanov",
      "type": "private"
    },
    "date": 1640995200,
    "text": "/start"
  }
}
```




**Ответ:**
```json
{
  "user": {
    "id": 1,
    "telegram_id": 123456789,
    "username": "ivan_ivanov",
    "first_name": "Иван",
    "last_name": "Иванов",
    "subscription_type": "free",
    "last_activity": "2024-01-15T10:30:00Z",
    "reminder_sent_at": null,
    "created_at": "2024-01-01T12:00:00Z"
  },
  "message_processed": true,
  "user_created": true,
  "user_updated": true
}
```




**Коды ответов:**
- `200` - Успешная обработка
- `400` - Некорректные данные
- `500` - Внутренняя ошибка сервера




### 2. Внутренние эндпоинты для бота




#### GET /menu-items




MENU




Получение структуры меню для пользователя.




**Параметры запроса:**
- `telegram_user_id` (int, обязательный) - ID пользователя в Telegram
- `parent_id` (int, необязательный) - ID родительского пункта меню (null для корневого уровня)




**Ответ:**
```json




MENU: LIST
{
  "items": [
    {
      "id": 1,
      "title": "Слуховые аппараты",
      "description": "Информация о слуховых аппаратах",
      "parent_id": null,
      "bot_message": "Выберите интересующий вас раздел:",
      "is_active": true,
      "access_level": "free",
      "children": [
        {
          "id": 2,
          "title": "Типы слуховых аппаратов",
          "description": "Обзор различных типов",
          "parent_id": 1,
          "bot_message": "Выберите тип:",
          "is_active": true,
          "access_level": "free"
        }
      ]
    }
  ]
}
```
MENU: ITEMS-DETAILS




#### GET /menu-items/{id}/content




Получение контента конкретного пункта меню.




**Параметры запроса:**
- `telegram_user_id` (int, обязательный) - ID пользователя в Telegram




**Ответ:**
```json
{
  "id": 1,
  "title": "Слуховые аппараты",
  "description": "Информация о слуховых аппаратах",
  "bot_message": "Вот полезная информация о слуховых аппаратах:",
  "content_files": [
    {
      "id": 1,
      "menu_item_id": 1,
      "content_type": "text",
      "content_text": "Слуховые аппараты помогают...",
      "content_url": null,
      "file_path": null,
      "file_size": null,
      "mime_type": null,
      "thumbnail_url": null,
      "is_primary": true,
      "sort_order": 1
    },
    {
      "id": 2,
      "menu_item_id": 1,
      "content_type": "image",
      "content_text": null,
      "content_url": "https://example.com/image.jpg",
      "file_path": null,
      "file_size": null,
      "mime_type": "image/jpeg",
      "thumbnail_url": "https://example.com/thumb.jpg",
      "is_primary": false,
      "sort_order": 2
    },
    {
      "id": 3,
      "menu_item_id": 1,
      "content_type": "video",
      "content_text": null,
      "content_url": "https://youtube.com/watch?v=123",
      "file_path": null,
      "file_size": null,
      "mime_type": null,
      "thumbnail_url": null,
      "is_primary": false,
      "sort_order": 3
    },
    {
      "id": 4,
      "menu_item_id": 1,
      "content_type": "pdf",
      "content_text": null,
      "content_url": null,
      "file_path": "/files/guide.pdf",
      "file_size": 1024000,
      "mime_type": "application/pdf",
      "thumbnail_url": null,
      "is_primary": false,
      "sort_order": 4
    }
  ]
}
```




#### POST /user-activities




USER: ACTIVITY
Запись активности пользователя.




**Тело запроса:**
```json
{
  "telegram_user_id": 123456789,
  "menu_item_id": 1,
  "activity_type": "view",
  "search_query": "слуховые аппараты"
}
```




**Ответ:**
```json
{
  "id": 123,
  "telegram_user_id": 123456789,
  "menu_item_id": 1,
  "activity_type": "view",
  "rating": null,
  "search_query": "слуховые аппараты"
}
```
















MENU: QUESTIONS




#### POST /user-questions




Создание вопроса от пользователя.




**Тело запроса:**
```json
{
  "telegram_user_id": 123456789,
  "question_text": "Как выбрать слуховой аппарат для ребенка?"
}
```




**Ответ:**
```json
{
  "id": 456,
  "telegram_user_id": 123456789,
  "question_text": "Как выбрать слуховой аппарат для ребенка?",
  "answer_text": null,
  "status": "pending",
  "answered_at": null
}
```




USER: RATING




#### POST /ratings




Оценка полезности материала.




**Тело запроса:**
```json
{
  "telegram_user_id": 123456789,
  "menu_item_id": 1,
  "rating": 5
}
```




**Ответ:**
```json
{
  "id": 789,
  "telegram_user_id": 123456789,
  "menu_item_id": 1,
  "activity_type": "rating",
  "rating": 5,
  "search_query": null
}
```
MENU: SEARCH
#### GET /search




Поиск по материалам.




**Параметры запроса:**
- `telegram_user_id` (int, обязательный) - ID пользователя в Telegram
- `query` (string, обязательный) - Поисковый запрос




**Ответ:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Слуховые аппараты",
      "description": "Информация о слуховых аппаратах",
      "parent_id": null,
      "bot_message": "Выберите интересующий вас раздел:",
      "is_active": true,
      "access_level": "free"
    }
  ]
}
```




### 3. Административные эндпоинты (требуют JWT)




#### Аутентификация




**Заголовки для административных запросов:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```








AUTH




#### POST /admin/auth/login




Аутентификация администратора.




**Тело запроса:**
```json
{
  "username": "admin",
  "password": "password123"
}
```




**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```




#### POST /admin/auth/refresh




Обновление токена доступа.




**Тело запроса:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```




**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```












USER: LIST
#### GET /admin/telegram-users




Получение списка пользователей Telegram.




**Параметры запроса:**
- `page` (int, необязательный) - Номер страницы (по умолчанию 1)
- `limit` (int, необязательный) - Количество записей на странице (по умолчанию 20)




**Ответ:**
```json
{
  "items": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "username": "ivan_ivanov",
      "first_name": "Иван",
      "last_name": "Иванов",
      "subscription_type": "free",
      "last_activity": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```
USER: Details




#### GET /admin/telegram-users/{id}




Получение информации о конкретном пользователе.




**Ответ:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "ivan_ivanov",
  "first_name": "Иван",
  "last_name": "Иванов",
  "subscription_type": "free",
  "last_activity": "2024-01-15T10:30:00Z",
  "reminder_sent_at": "2024-01-10T09:00:00Z",
  "created_at": "2024-01-01T12:00:00Z",
  "activities_count": 25,
  "questions_count": 3
}
```
ADMIN: MENU-LIST




#### GET /admin/menu-items




Получение списка пунктов меню.




**Параметры запроса:**
- `page` (int, необязательный) - Номер страницы (по умолчанию 1)
- `limit` (int, необязательный) - Количество записей на странице (по умолчанию 20)




**Ответ:**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Слуховые аппараты",
      "description": "Информация о слуховых аппаратах",
      "parent_id": null,
      "bot_message": "Выберите интересующий вас раздел:",
      "is_active": true,
      "access_level": "free",
      "view_count": 150,
      "download_count": 45,
      "rating_sum": 450,
      "rating_count": 100,
      "average_rating": 4.5,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-15T16:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```




ADMIN: ITEM




#### POST /admin/menu-items




Создание нового пункта меню.




**Тело запроса:**
```json
{
  "title": "Новый раздел",
  "description": "Описание нового раздела",
  "parent_id": 1,
  "bot_message": "Сообщение бота для этого раздела",
  "access_level": "free",
  "is_active": true
}
```




**Ответ:**
```json
{
  "id": 123,
  "title": "Новый раздел",
  "description": "Описание нового раздела",
  "parent_id": 1,
  "bot_message": "Сообщение бота для этого раздела",
  "is_active": true,
  "access_level": "free",
  "view_count": 0,
  "download_count": 0,
  "rating_sum": 0,
  "rating_count": 0,
  "average_rating": null,
  "created_at": "2024-01-15T15:00:00Z",
  "updated_at": "2024-01-15T15:00:00Z"
}
```












#### PUT /admin/menu-items/{id}




Обновление пункта меню.




**Тело запроса:**
```json
{
  "title": "Обновленное название",
  "description": "Обновленное описание",
  "bot_message": "Обновленное сообщение бота",
  "access_level": "premium",
  "is_active": true
}
```




**Ответ:**
```json
{
  "id": 123,
  "title": "Обновленное название",
  "description": "Обновленное описание",
  "parent_id": 1,
  "bot_message": "Обновленное сообщение бота",
  "is_active": true,
  "access_level": "premium",
  "view_count": 150,
  "download_count": 45,
  "rating_sum": 450,
  "rating_count": 100,
  "average_rating": 4.5,
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-15T16:00:00Z"
}
```




#### DELETE /admin/menu-items/{id}




Удаление пункта меню.




**Ответ:**
```
204 No Content
```












ADMIN: FILE




#### GET /admin/menu-items/{id}/content-files




Получение файлов контента для пункта меню.




**Ответ:**
```json
{
  "items": [
    {
      "id": 1,
      "menu_item_id": 1,
      "content_type": "text",
      "content_text": "Текстовый контент",
      "content_url": null,
      "file_path": null,
      "file_size": null,
      "mime_type": null,
      "thumbnail_url": null,
      "is_primary": true,
      "sort_order": 1,
      "created_at": "2024-01-01T12:00:00Z"
    },
    {
      "id": 2,
      "menu_item_id": 1,
      "content_type": "image",
      "content_text": null,
      "content_url": "https://example.com/image.jpg",
      "file_path": null,
      "file_size": null,
      "mime_type": "image/jpeg",
      "thumbnail_url": "https://example.com/thumb.jpg",
      "is_primary": false,
      "sort_order": 2,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```




#### POST /admin/menu-items/{id}/content-files




Добавление файла контента к пункту меню.




**Тело запроса:**
```json
{
  "content_type": "text",
  "content_text": "Новый текстовый контент",
  "sort_order": 3
}
```




**Ответ:**
```json
{
  "id": 123,
  "menu_item_id": 1,
  "content_type": "text",
  "content_text": "Новый текстовый контент",
  "content_url": null,
  "file_path": null,
  "file_size": null,
  "mime_type": null,
  "thumbnail_url": null,
  "is_primary": false,
  "sort_order": 3,
  "created_at": "2024-01-15T17:00:00Z"
}
```




#### PUT /admin/content-files/{id}




Обновление файла контента.




**Тело запроса:**
```json
{
  "content_text": "Обновленный текстовый контент",
  "sort_order": 1
}
```




**Ответ:**
```json
{
  "id": 123,
  "menu_item_id": 1,
  "content_type": "text",
  "content_text": "Обновленный текстовый контент",
  "content_url": null,
  "file_path": null,
  "file_size": null,
  "mime_type": null,
  "thumbnail_url": null,
  "is_primary": true,
  "sort_order": 1,
  "created_at": "2024-01-01T12:00:00Z"
}
```




#### DELETE /admin/content-files/{id}




Удаление файла контента.




**Ответ:**
```
204 No Content
```




ADMIN: QUESTIONS




#### GET /admin/user-questions




Получение списка вопросов от пользователей.




**Параметры запроса:**
- `page` (int, необязательный) - Номер страницы (по умолчанию 1)
- `limit` (int, необязательный) - Количество записей на странице (по умолчанию 20)




**Ответ:**
```json
{
  "items": [
    {
      "id": 1,
      "telegram_user_id": 123456789,
      "question_text": "Как выбрать слуховой аппарат для ребенка?",
      "answer_text": null,
      "status": "pending",
      "created_at": "2024-01-15T10:00:00Z",
      "answered_at": null
    }
  ],
  "total": 25,
  "page": 1,
  "limit": 20,
  "pages": 2
}
```




#### PUT /admin/user-questions/{id}




Ответ на вопрос пользователя.




**Тело запроса:**
```json
{
  "answer_text": "Для выбора слухового аппарата для ребенка необходимо..."
}
```




**Ответ:**
```json
{
  "id": 1,
  "telegram_user_id": 123456789,
  "question_text": "Как выбрать слуховой аппарат для ребенка?",
  "answer_text": "Для выбора слухового аппарата для ребенка необходимо...",
  "status": "answered",
  "created_at": "2024-01-15T10:00:00Z",
  "answered_at": "2024-01-15T19:00:00Z"
}
```




ADMIN: ANALYTICS




#### GET /admin/analytics




Получение базовой аналитики и статистики.




**Параметры запроса:**
- `period` (string, необязательный) - Период (day, week, month, year)
- `start_date` (string, необязательный) - Начальная дата (ISO 8601)
- `end_date` (string, необязательный) - Конечная дата (ISO 8601)




**Ответ:**
```json
{
  "users": {
    "total": 1250,
    "active_today": 45,
    "active_week": 320,
    "active_month": 890
  },
  "content": {
    "total_menu_items": 50,
    "most_viewed": [
      {
        "id": 1,
        "title": "Слуховые аппараты",
        "view_count": 150,
        "download_count": 45,
        "average_rating": 4.5
      }
    ],
    "most_rated": [
      {
        "id": 2,
        "title": "Типы слуховых аппаратов",
        "average_rating": 4.8,
        "rating_count": 25
      }
    ]
  },
  "activities": {
    "total_views": 5420,
    "total_downloads": 890,
    "total_ratings": 340,
    "search_queries": [
      {
        "query": "слуховые аппараты",
        "count": 45
      }
    ]
  },
  "questions": {
    "total": 150,
    "pending": 25,
    "answered": 125
  }
}
```
ADMIN: NOTIFICATIONS
NOTIFICATIONS: LIST
#### POST /admin/notifications




Отправка уведомления пользователю.




**Тело запроса:**
```json
{
  "telegram_user_id": 123456789,
  "message": "Напоминание: не забудьте проверить новые материалы!"
}
```




**Ответ:**
```json
{
  "id": 789,
  "telegram_user_id": 123456789,
  "message": "Напоминание: не забудьте проверить новые материалы!",
  "status": "sent",
  "created_at": "2024-01-15T20:00:00Z",
  "sent_at": "2024-01-15T20:00:00Z",
  "template_id": 1
}
```




#### GET /admin/notifications




Получение списка уведомлений.




**Параметры запроса:**
- `page` (int, необязательный) - Номер страницы (по умолчанию 1)
- `limit` (int, необязательный) - Количество записей на странице (по умолчанию 20)




**Ответ:**
```json
{
  "items": [
    {
      "id": 789,
      "telegram_user_id": 123456789,
      "message": "Напоминание: не забудьте проверить новые материалы!",
      "status": "sent",
      "created_at": "2024-01-15T20:00:00Z",
      "sent_at": "2024-01-15T20:00:00Z",
      "template_id": 1
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```
NOTIFICATIONS: ACTIONS




#### GET /admin/notifications/{id}




Получение уведомления.




**Ответ:**
```json
{
  "id": 789,
  "telegram_user_id": 123456789,
  "message": "Напоминание: не забудьте проверить новые материалы!",
  "status": "sent",
  "created_at": "2024-01-15T20:00:00Z",
  "sent_at": "2024-01-15T20:00:00Z",
  "template_id": 1
}
```




#### PUT /admin/notifications/{id}




Обновление уведомления.




**Тело запроса:**
```json
{
  "status": "sent",
  "sent_at": "2024-01-15T20:00:00Z"
}
```




**Ответ:**
```json
{
  "id": 789,
  "telegram_user_id": 123456789,
  "message": "Напоминание: не забудьте проверить новые материалы!",
  "status": "sent",
  "created_at": "2024-01-15T20:00:00Z",
  "sent_at": "2024-01-15T20:00:00Z",
  "template_id": 1
}
```




#### DELETE /admin/notifications/{id}




Удаление уведомления.




**Ответ:**
```
204 No Content
```




#### GET /admin/reminder-templates




Получение шаблонов напоминаний.




NOTIFICATIONS: TEMPLATES




**Ответ:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Еженедельное напоминание",
      "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас.",
      "is_active": true,
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```




#### POST /admin/reminder-templates




Создание шаблона напоминания.




**Тело запроса:**
```json
{
  "name": "Новый шаблон",
  "message_template": "Текст напоминания",
  "is_active": true
}
```




**Ответ:**
```json
{
  "id": 2,
  "name": "Новый шаблон",
  "message_template": "Текст напоминания",
  "is_active": true,
  "created_at": "2024-01-15T20:00:00Z",
  "updated_at": "2024-01-15T20:00:00Z"
}
```




#### PUT /admin/reminder-templates/{id}




Обновление шаблона напоминания.




**Тело запроса:**
```json
{
  "name": "Обновленный шаблон",
  "message_template": "Обновленный текст напоминания",
  "is_active": false
}
```




**Ответ:**
```json
{
  "id": 2,
  "name": "Обновленный шаблон",
  "message_template": "Обновленный текст напоминания",
  "is_active": false,
  "created_at": "2024-01-15T20:00:00Z",
  "updated_at": "2024-01-15T21:00:00Z"
}
```




#### DELETE /admin/reminder-templates/{id}




Удаление шаблона напоминания.




**Ответ:**
```
204 No Content
```




## Коды ошибок




### Общие коды ошибок




- `400` - Bad Request - Некорректные данные запроса
- `401` - Unauthorized - Требуется аутентификация
- `403` - Forbidden - Недостаточно прав доступа
- `404` - Not Found - Ресурс не найден
- `422` - Unprocessable Entity - Ошибка валидации данных
- `500` - Internal Server Error - Внутренняя ошибка сервера




#### GET /webhook/telegram/health




Проверка работоспособности webhook эндпоинта.




**Ответ:**
```json
{
  "status": "ok",
  "message": "Webhook endpoint is healthy"
}
```




### Формат ошибок




```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Ошибка валидации данных",
    "details": [
      {
        "field": "title",
        "message": "Поле обязательно для заполнения"
      }
    ]
  }
}
```

