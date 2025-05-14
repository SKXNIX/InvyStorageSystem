-- Функция для триггера
CREATE OR REPLACE FUNCTION update_product_quantity()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.operation_type = 'incoming' THEN
            UPDATE products 
            SET current_quantity = current_quantity + NEW.quantity,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = NEW.product_id;
        ELSIF NEW.operation_type = 'outgoing' THEN
            -- Проверка, чтобы остаток не ушел в минус
            IF (SELECT current_quantity FROM products WHERE product_id = NEW.product_id) >= NEW.quantity THEN
                UPDATE products 
                SET current_quantity = current_quantity - NEW.quantity,
                    updated_at = CURRENT_TIMESTAMP
                WHERE product_id = NEW.product_id;
            ELSE
                RAISE EXCEPTION 'Недостаточно товара на складе (ID: %)', NEW.product_id;
            END IF;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        -- Откат изменений при удалении операции
        IF OLD.operation_type = 'incoming' THEN
            UPDATE products 
            SET current_quantity = current_quantity - OLD.quantity,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = OLD.product_id;
        ELSIF OLD.operation_type = 'outgoing' THEN
            UPDATE products 
            SET current_quantity = current_quantity + OLD.quantity,
                updated_at = CURRENT_TIMESTAMP
            WHERE product_id = OLD.product_id;
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера
CREATE TRIGGER operations_quantity_trigger
AFTER INSERT OR DELETE ON operations
FOR EACH ROW EXECUTE FUNCTION update_product_quantity();