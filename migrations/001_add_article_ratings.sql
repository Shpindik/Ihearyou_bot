-- Миграция для добавления таблицы article_ratings
CREATE TABLE IF NOT EXISTS article_ratings (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    article_name VARCHAR(255) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, article_name)
);

-- Создаем индекс для быстрого поиска по user_id
CREATE INDEX IF NOT EXISTS idx_article_ratings_user_id ON article_ratings(user_id);

-- Создаем индекс для быстрого поиска по article_name
CREATE INDEX IF NOT EXISTS idx_article_ratings_article_name ON article_ratings(article_name);
