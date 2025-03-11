DROP DATABASE IF EXISTS Vendors;
CREATE DATABASE Vendors;

USE Vendors;

-- Vendors Table
CREATE TABLE Vendors (
    VendorID INT AUTO_INCREMENT PRIMARY KEY,
    VendorName VARCHAR(255) NOT NULL,
    Location VARCHAR(255) NOT NULL,
    OpeningHours VARCHAR(255) NOT NULL,
    ImageURL VARCHAR(2048) NOT NULL,
    Cuisine VARCHAR(255) NOT NULL,
    Rating DECIMAL(3, 2) DEFAULT 0.00 -- Rating between 0.00 and 5.00
);

-- Insert sample vendors
INSERT INTO Vendors (VendorID,VendorName, Location, OpeningHours, ImageURL, Cuisine) VALUES 
(1,'Pasta Express (SMU)', '40 Stamford Rd, Singapore 178908','Monday-Friday: 10am-8pm','https://scontent.fsin10-1.fna.fbcdn.net/v/t39.30808-6/481264475_939156428419388_6703251991519933088_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=cc71e4&_nc_ohc=QdO8WmSXs7wQ7kNvgF6L1kU&_nc_oc=Adgc758KvN4BBMbCMJRseXRw4dBn8QnGNuMtv20VNax6kPsjnTfkKYt_8KnZ64K6ZHI&_nc_zt=23&_nc_ht=scontent.fsin10-1.fna&_nc_gid=Aa-6eUle8QFnVCphrD0VEnl&oh=00_AYHVqq_YAgr27PWQSfquNO95r1dvI_Nve9PGHonv-dfdRQ&oe=67D23977','Western'),
(2,"PARK'S KITCHEN(SMU CONNEXTION)",'40 Stamford Rd, #01-02','Monday-Friday: 10:30am-8pm','../images/paiks.png','Korean'),
(3,'Kuro Kare','80 Stamford Road #B1-65 SMU School of Information Systems, 178902','Monday-Friday: 11am-8pm','https://dam.mediacorp.sg/image/upload/s--UluaRJKo--/f_auto,q_auto/v1/mediacorp/8days/image/2023/07/21/kuro-kare_kel_9366_1.jpg?itok=yPkW13h_','Japanese');

-- MenuItems Table
CREATE TABLE MenuItems (
    ItemID INT AUTO_INCREMENT PRIMARY KEY,
    VendorID INT,
    ItemName VARCHAR(255) NOT NULL,
    Description TEXT,
    Price DECIMAL(10, 2) NOT NULL,
    Category VARCHAR(100),
    ImageURL VARCHAR(2048),
    FOREIGN KEY (VendorID) REFERENCES Vendors(VendorID)
);

INSERT INTO MenuItems (VendorID, ItemName, Description, Price, Category, ImageURL) VALUES 
(1, 1, 'Laksa Cream Sauce + Spaghetti', '', 5.80, 'Must Try New Flavour! For A Limited Time Only!', 'https://images.deliveryhero.io/image/fd-sg/Products/46065581.jpg??width=800'),
(2, 1, 'Smoked Duck Aglio Olio', 'Aglio Olio + Spaghetti, Smoked Duck Breast, Sous Vide Egg, Spinach, Mushroom', 9.00, 'Pasta', 'https://images.deliveryhero.io/image/fd-sg/Products/5368047.jpg??width=800'),
(3, 1, 'Carbonara', 'Cream Sauce + Organic Spaghetti, Pork Bacon, Sous Vide Egg, Spinach, Button Mushroom', 11.80, 'Pasta', 'https://images.deliveryhero.io/image/fd-sg/Products/37909329.jpg??width=800'),
(4, 1, 'Chicken Alfredo', 'Cream Sauce + Organic Spaghetti, Chicken Thigh, Sous Vide Egg, Spinach, Button Mushroom', 11.80, 'Pasta', 'https://images.deliveryhero.io/image/fd-sg/Products/37909330.jpg??width=800'),
(5, 1, 'Meat Lovers', 'Cream Sauce + Organic Spaghetti, Smoked Duck, Pork Bacon, Chicken Thigh, Sous Vide Egg', 12.60, 'Pasta', 'https://images.deliveryhero.io/image/fd-sg/Products/37909336.jpg??width=800');

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