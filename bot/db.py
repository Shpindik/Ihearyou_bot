import os

import asyncpg

DB_NAME = os.getenv("POSTGRES_DB", "postgres_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres_password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", 5432))


# Сохраняем данные пользователя
async def save_user_data(
    user_id: int,
    username: str,
    fullname: str,
):
    conn = await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )
    try:
        await conn.execute(
            """
            INSERT INTO users (
                user_id,
                username,
                fullname
            )
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                fullname = EXCLUDED.fullname
            """,
            user_id,
            username,
            fullname,
        )
    finally:
        await conn.close()


# Сохраняем оценку статьи
async def save_article_rating(
    user_id: int,
    article_name: str,
    rating: int,
):
    conn = await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )
    try:
        await conn.execute(
            """
            INSERT INTO article_ratings (
                user_id,
                article_name,
                rating
            )
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id, article_name) DO UPDATE SET
                rating = EXCLUDED.rating,
                created_at = now()
            """,
            user_id,
            article_name,
            rating,
        )
    finally:
        await conn.close()
