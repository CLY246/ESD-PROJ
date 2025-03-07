CREATE DATABASE Vendors;

USE Vendors;


-- Vendors Table
CREATE TABLE Vendors (
    VendorID INT AUTO_INCREMENT PRIMARY KEY,
    VendorName VARCHAR(255) NOT NULL,
    Location VARCHAR(255) NOT NULL,
    ContactInfo VARCHAR(255) NOT NULL,
    Rating DECIMAL(3, 2) DEFAULT 0.00 -- Rating between 0.00 and 5.00
);

-- MenuItems Table
CREATE TABLE MenuItems (
    ItemID INT AUTO_INCREMENT PRIMARY KEY,
    VendorID INT,
    ItemName VARCHAR(255) NOT NULL,
    Description TEXT,
    Price DECIMAL(10, 2) NOT NULL,
    Category VARCHAR(100),
    ImageURL VARCHAR(255),
    FOREIGN KEY (VendorID) REFERENCES Vendors(VendorID)
);

-- Inventory Table
CREATE TABLE Inventory (
    InventoryID INT AUTO_INCREMENT PRIMARY KEY,
    VendorID INT,
    ItemID INT,
    QuantityAvailable INT NOT NULL,
    LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (VendorID) REFERENCES Vendors(VendorID),
    FOREIGN KEY (ItemID) REFERENCES MenuItems(ItemID)
);