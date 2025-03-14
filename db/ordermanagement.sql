-- Create the OrderManagement database
DROP DATABASE IF EXISTS OrderManagement;
CREATE DATABASE IF NOT EXISTS OrderManagement;
USE ordermanagement;

-- Create Orders Table
CREATE TABLE Orders (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL, -- Reference to user
    OrderDateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    OrderStatus VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', etc.
    TransactionID VARCHAR(255) NOT NULL,
    FOREIGN KEY (UserID) REFERENCES user.users(id) ON DELETE CASCADE
);

-- Create OrderItems Table
CREATE TABLE OrderItems (
    OrderItemID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT NOT NULL,
    ItemID INT NOT NULL, -- Reference to menu item or product
    Quantity INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    VendorID INT NOT NULL, 
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE
);

-- Create OrderQueue Table
CREATE TABLE OrderQueue (
    QueueID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT NOT NULL UNIQUE, 
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    EstimatedWaitTime INT,
    Status ENUM('Queued', 'Processing', 'Completed') DEFAULT 'Queued',
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE
);

-- Insert Orders (UserID must exist in users table)
INSERT INTO Orders (UserID, TotalAmount, OrderStatus, TransactionID)
VALUES 
(4, 150.00, 'completed', 'TXN11223'),
(5, 75.00, 'pending', 'TXN33445'),
(6, 120.00, 'completed', 'TXN55678'),
(7, 90.25, 'pending', 'TXN77889'),
(8, 45.50, 'completed', 'TXN99001'),
(9, 60.00, 'completed', 'TXN22334');

-- Insert OrderItems (OrderID must match those generated in Orders table)
INSERT INTO OrderItems (OrderID, ItemID, Quantity, Price, VendorID)
VALUES 
(1, 1, 1, 50.00, 1),
(2, 6, 2, 30.00, 2),
(3, 11, 1, 40.00, 3),
(4, 16, 2, 60.00, 4),
(5, 21, 3, 15.00, 5);

-- Insert OrderQueue Data
INSERT INTO OrderQueue (OrderID, EstimatedWaitTime, Status) VALUES
(1, 10, 'Queued'),
(2, 5, 'Processing'),
(3, 8, 'Queued'),
(4, 12, 'Queued'),
(5, 7, 'Processing');
