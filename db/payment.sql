
-- Create the Payment database
DROP DATABASE IF EXISTS Payment;
CREATE DATABASE Payment;

-- Select the database
USE Payment;

-- Transactions Table with Foreign Key Reference to Orders
CREATE TABLE Transactions (
    TransactionID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentMethod ENUM('PayNow') NOT NULL, -- ENUM to enforce the only method 'PayNow'
    PaymentStatus VARCHAR(50), -- e.g., "Pending", "Successful", "Failed"
    TransactionDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (OrderID) REFERENCES ordermanagement.Orders(OrderID) ON DELETE CASCADE
);

-- Insert data into the Transactions table
-- Insert data into the Transactions table
INSERT INTO Transactions (OrderID, Amount, PaymentMethod, PaymentStatus)
VALUES 
(1, 150.00, 'PayNow', 'Successful'),
(2, 75.00, 'PayNow', 'Pending'),
(3, 120.00, 'PayNow', 'Successful'),
(4, 90.25, 'PayNow', 'Failed'),
(5, 45.50, 'PayNow', 'Successful'),
(6, 120.00, 'PayNow', 'Pending'),
(7, 90.25, 'PayNow', 'Successful'),
(8, 60.75, 'PayNow', 'Successful'),
(9, 120.00, 'PayNow', 'Failed'),
(10, 75.00, 'PayNow', 'Pending');
