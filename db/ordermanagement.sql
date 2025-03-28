-- SET FOREIGN_KEY_CHECKS = 0;

-- DROP DATABASE IF EXISTS OrderManagement;

-- SET FOREIGN_KEY_CHECKS = 1;


-- -- Create the OrderManagement database
-- DROP DATABASE IF EXISTS OrderManagement;
-- CREATE DATABASE OrderManagement;
-- USE OrderManagement;

-- -- Create Orders Table
-- CREATE TABLE Orders (
--     OrderID INT PRIMARY KEY AUTO_INCREMENT,
--     UserID INT NOT NULL, -- Reference to user, no FK constraint
--     OrderDateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     TotalAmount DECIMAL(10, 2) NOT NULL,
--     OrderStatus VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', etc.
--     TransactionID VARCHAR(255) NOT NULL
-- );

-- -- Create OrderItems Table
-- CREATE TABLE OrderItems (
--     OrderItemID INT PRIMARY KEY AUTO_INCREMENT,
--     OrderID INT NOT NULL,
--     ItemID INT NOT NULL, -- Reference to menu item or product
--     Quantity INT NOT NULL,
--     Price DECIMAL(10, 2) NOT NULL,
--     VendorID INT NOT NULL
-- );

-- -- Create OrderQueue Table
-- CREATE TABLE OrderQueue (
--     QueueID INT PRIMARY KEY AUTO_INCREMENT,
--     OrderID INT NOT NULL UNIQUE, 
--     Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     EstimatedWaitTime INT,
--     Status ENUM('Queued', 'Processing', 'Completed') DEFAULT 'Queued'
-- );

-- -- Insert Orders
-- INSERT INTO Orders (UserID, TotalAmount, OrderStatus, TransactionID)
-- VALUES 
-- (4, 150.00, 'completed', 'TXN11223'),
-- (5, 75.00, 'pending', 'TXN33445'),
-- (6, 120.00, 'completed', 'TXN55678'),
-- (7, 90.25, 'pending', 'TXN77889'),
-- (8, 45.50, 'completed', 'TXN99001'),
-- (9, 60.00, 'completed', 'TXN22334');

-- -- Insert OrderItems
-- INSERT INTO OrderItems (OrderID, ItemID, Quantity, Price, VendorID)
-- VALUES 
-- (1, 1, 1, 50.00, 1),
-- (2, 6, 2, 30.00, 2),
-- (3, 11, 1, 40.00, 3),
-- (4, 16, 2, 60.00, 4),
-- (5, 21, 3, 15.00, 5);

-- -- Insert OrderQueue Data
-- INSERT INTO OrderQueue (OrderID, EstimatedWaitTime, Status) VALUES
-- (1, 10, 'Queued'),
-- (2, 5, 'Processing'),
-- (3, 8, 'Queued'),
-- (4, 12, 'Queued'),
-- (5, 7, 'Processing');



-- Create the OrderManagement database
DROP DATABASE IF EXISTS OrderManagement;
CREATE DATABASE OrderManagement;
USE OrderManagement;

-- No need to create database, already exists in Supabase

CREATE TABLE orders (
    "OrderID" SERIAL PRIMARY KEY,
    "UserID" VARCHAR NOT NULL,
    "OrderDateTime" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "TotalAmount" NUMERIC(10, 2) NOT NULL,
    "OrderStatus" VARCHAR(50) DEFAULT 'pending',
    "TransactionID" VARCHAR(255) NOT NULL
);

CREATE TABLE order_items (
    "OrderItemID" SERIAL PRIMARY KEY,
    "OrderID" INTEGER NOT NULL REFERENCES orders("OrderID"),
    "ItemID" INTEGER NOT NULL,
    "Quantity" INTEGER NOT NULL,
    "Price" NUMERIC(10, 2) NOT NULL,
    "StoreID" INTEGER NOT NULL
);

CREATE TYPE order_status_enum AS ENUM ('Queued', 'Processing', 'Completed');

CREATE TABLE order_queue (
    "QueueID" SERIAL PRIMARY KEY,
    "OrderID" INTEGER UNIQUE NOT NULL,
    "Timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "EstimatedWaitTime" INTEGER,
    "Status" order_status_enum DEFAULT 'Queued'
);


INSERT INTO orders ("UserID", "TotalAmount", "OrderStatus", "TransactionID")
VALUES 
('4', 150.00, 'completed', 'TXN11223'),
('5', 75.00, 'pending', 'TXN33445'),
('6', 120.00, 'completed', 'TXN55678'),
('7', 90.25, 'pending', 'TXN77889'),
('8', 45.50, 'completed', 'TXN99001'),
('9', 60.00, 'completed', 'TXN22334');


INSERT INTO order_items ("OrderID", "ItemID", "Quantity", "Price", "StoreID")
VALUES 
(1, 1, 1, 50.00, 1),
(2, 6, 2, 30.00, 2),
(3, 11, 1, 40.00, 3),
(4, 16, 2, 60.00, 4),
(5, 21, 3, 15.00, 5),
(6, 4, 2, 30.00, 1);

INSERT INTO order_queue ("OrderID", "EstimatedWaitTime", "Status")
VALUES 
(1, 10, 'Queued'),
(2, 5, 'Processing'),
(3, 8, 'Queued'),
(4, 12, 'Queued'),
(5, 7, 'Processing'),
(6, 6, 'Completed');




-- SELECT 
--     table_name,
--     column_name,
--     data_type
-- FROM 
--     information_schema.columns
-- WHERE 
--     table_schema = 'public'
-- ORDER BY 
--     table_name,
--     ordinal_position;
