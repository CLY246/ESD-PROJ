-- Create the database
CREATE DATABASE IF NOT EXISTS ordermanagement;
USE ordermanagement;

-- Orders Table
CREATE TABLE Orders (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL, -- Reference to user
    OrderDateTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    OrderStatus VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', etc.
    TransactionID VARCHAR(255) NOT NULL
);

-- OrderItems Table
CREATE TABLE OrderItems (
    OrderItemID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT NOT NULL,
    ItemID INT NOT NULL, -- Reference to menu item or product
    Quantity INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    StoreID INT NOT NULL, -- Reference to vendor/store
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE
);

-- Insert Additional Dummy Data into Orders
INSERT INTO Orders (UserID, TotalAmount, OrderStatus, TransactionID)
VALUES 
(4, 150.00, 'completed', 'TXN11223'),
(5, 75.00, 'pending', 'TXN33445'),
(6, 120.00, 'completed', 'TXN55678'),
(7, 90.25, 'pending', 'TXN77889'),
(8, 45.50, 'completed', 'TXN99001');

-- Insert Additional Dummy Data into OrderItems
INSERT INTO OrderItems (OrderID, ItemID, Quantity, Price, StoreID)
VALUES 
(3, 104, 1, 50.00, 5004),
(4, 105, 2, 30.00, 5005),
(5, 106, 1, 40.00, 5006),
(6, 107, 2, 60.00, 5007),
(7, 108, 3, 15.00, 5008),
(8, 109, 1, 45.50, 5009);

