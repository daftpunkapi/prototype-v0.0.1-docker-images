DROP TABLE pending_orders_table;

CREATE TABLE pending_orders_table (
rest_id VARCHAR(25) PRIMARY KEY,
pending_count INT);

SELECT * FROM pending_orders_table;

SELECT sum(pending_count) FROM pending_orders_table;
