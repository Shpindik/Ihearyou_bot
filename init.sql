CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE,
    username VARCHAR(100),
    fullname VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO admin_users (username, password_hash, role)
VALUES ('admin', '$2b$12$1KdZ/Fai5KKHotfLKJ6WoeNFmAwtY4vo88.yu0Ts4cOiVxMnf0cdy', 'admin')
ON CONFLICT (username) DO NOTHING;

ALTER DATABASE ihearyou_db SET timezone TO 'Europe/Moscow';
