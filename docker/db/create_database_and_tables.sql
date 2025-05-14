-- Создание базы данных
CREATE DATABASE "stockDB";

-- Таблица пользователей
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'storekeeper')),
    avatar BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица категорий товаров
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица поставщиков
CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица товаров
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id) ON DELETE RESTRICT,
    unit_of_measure VARCHAR(20) NOT NULL,
    description TEXT,
    storage_location VARCHAR(100) NOT NULL,
    min_quantity INTEGER NOT NULL DEFAULT 0,
    current_quantity INTEGER NOT NULL DEFAULT 0,
    image BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица операций
CREATE TABLE operations (
    operation_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
    operation_type VARCHAR(10) NOT NULL CHECK (operation_type IN ('incoming', 'outgoing')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    operation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    document_number VARCHAR(100) NOT NULL,
    supplier_id INTEGER REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    recipient_name VARCHAR(255),
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
