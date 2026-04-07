CREATE TABLE IF NOT EXISTS book (
    id        SERIAL PRIMARY KEY,
    title     VARCHAR(255) NOT NULL,
    author    VARCHAR(255) NOT NULL,
    source    VARCHAR(100),
    type      VARCHAR(50),
    status    VARCHAR(50)  DEFAULT 'Finished',
    featuring VARCHAR(255)
);
