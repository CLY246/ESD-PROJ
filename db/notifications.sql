-- -- Create the database
-- DROP DATABASE IF EXISTS Notifications;
-- CREATE DATABASE Notifications;

-- -- Select the database
-- USE Notifications;


-- -- Notification Table
-- CREATE TABLE Notifications (
--     NotificationID INT PRIMARY KEY AUTO_INCREMENT,
--     UserID INT NOT NULL,
--     OrderID INT NOT NULL, -- Make it NOT NULL if always tied to an order
--     NotificationType ENUM('Order Update', 'Payment Confirmation', 'Delivery Update', 'Promotion') NOT NULL, -- ENUM for fixed values
--     Message TEXT,
--     Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     IsRead BOOLEAN DEFAULT FALSE
-- );

-- -- activity log data
-- INSERT INTO Notifications (UserID, OrderID, NotificationType, Message, IsRead) 
-- VALUES
-- (1, 101, 'Order Update', 'Your order has been placed successfully.', FALSE),
-- (2, 102, 'Payment Confirmation', 'Your payment for Order 102 has been received.', TRUE),
-- (3, 103, 'Order Update', 'Your order is ready.', FALSE),
-- (4, 104, 'Order Update', 'Your order has been placed successfully.', FALSE),
-- (5, 105, 'Payment Confirmation', 'Your payment for Order 105 has been received.', TRUE),
-- (7, 107, 'Order Update', 'Your order has been placed successfully.', FALSE),
-- (8, 108, 'Payment Confirmation', 'Your payment for Order 108 has been received.', TRUE),
-- (10, 110, 'Order Update', 'Your order has been placed successfully.', FALSE);





-- Create the database
DROP DATABASE IF EXISTS notification;
CREATE DATABASE notification;

-- Select the database
USE notification;  -- This should match the database name created above.

-- Notification Table
CREATE TABLE notifications (  -- Use lowercase 'notifications' as per the table name in your code
    NotificationID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    OrderID INT NOT NULL, -- Make it NOT NULL if always tied to an order
    NotificationType ENUM('Order Update', 'Payment Confirmation', 'Delivery Update', 'Promotion') NOT NULL, -- ENUM for fixed values
    Message TEXT,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IsRead BOOLEAN DEFAULT FALSE
);

-- Activity log data
INSERT INTO notifications (UserID, OrderID, NotificationType, Message, IsRead)  -- Table name 'notifications' in lowercase
VALUES
(1, 101, 'Order Update', 'Your order has been placed successfully.', FALSE),
(2, 102, 'Payment Confirmation', 'Your payment for Order 102 has been received.', TRUE),
(3, 103, 'Order Update', 'Your order is ready.', FALSE),
(4, 104, 'Order Update', 'Your order has been placed successfully.', FALSE),
(5, 105, 'Payment Confirmation', 'Your payment for Order 105 has been received.', TRUE),
(7, 107, 'Order Update', 'Your order has been placed successfully.', FALSE),
(8, 108, 'Payment Confirmation', 'Your payment for Order 108 has been received.', TRUE),
(10, 110, 'Order Update', 'Your order has been placed successfully.', FALSE);
