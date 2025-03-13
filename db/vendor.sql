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

-- Vendor Table Data
INSERT INTO Vendors (VendorID,VendorName, Location, OpeningHours, ImageURL, Cuisine) VALUES 
(1,'Pasta Express (SMU)', '40 Stamford Rd, Singapore 178908','Monday-Friday: 10am-8pm','https://scontent.fsin10-1.fna.fbcdn.net/v/t39.30808-6/481264475_939156428419388_6703251991519933088_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=cc71e4&_nc_ohc=QdO8WmSXs7wQ7kNvgF6L1kU&_nc_oc=Adgc758KvN4BBMbCMJRseXRw4dBn8QnGNuMtv20VNax6kPsjnTfkKYt_8KnZ64K6ZHI&_nc_zt=23&_nc_ht=scontent.fsin10-1.fna&_nc_gid=Aa-6eUle8QFnVCphrD0VEnl&oh=00_AYHVqq_YAgr27PWQSfquNO95r1dvI_Nve9PGHonv-dfdRQ&oe=67D23977','Western'),
(2,"PARK'S KITCHEN(SMU CONNEXTION)",'40 Stamford Rd, #01-02','Monday-Friday: 10:30am-8pm','../images/paiks.png','Korean'),
(3,'Kuro Kare','80 Stamford Road #B1-65 SMU School of Information Systems, 178902','Monday-Friday: 11am-8pm','https://dam.mediacorp.sg/image/upload/s--UluaRJKo--/f_auto,q_auto/v1/mediacorp/8days/image/2023/07/21/kuro-kare_kel_9366_1.jpg?itok=yPkW13h_','Japanese'),
(4, 'Khoon Coffeehouse Express SMU', '90 Stamford Rd, #01-72, Singapore 178903', 'Monday-Saturday: 8am-8pm', 'https://eatbook.sg/wp-content/uploads/2022/12/khoon-coffeehouse-express-storefront.jpg', 'Western'),
(5, 'Each A Cup x GROUNDED - FLOOR IS LAVA @ SMU', '70 Stamford Rd, B1-45, Singapaore 178901', 'Monday-Sunday: 9am-9pm', 'https://lh3.googleusercontent.com/p/AF1QipMBubySaEd7JTCWnw1yjtNRlMRNgSbD-DMYZMpo=s1360-w1360-h1020', 'Beverage');

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

-- Inventory Table Data
INSERT INTO MenuItems (ItemID, VendorID, ItemName, Description, Price, Category, ImageURL) VALUES 
(1, 1, 'Laksa Cream Sauce + Spaghetti', '', 5.80, 'Must Try New Flavour! For A Limited Time Only!', 'https://images.deliveryhero.io/image/fd-sg/Products/46065581.jpg??width=800'),
(2, 1, 'Smoked Duck Aglio Olio', 'Aglio Olio + Spaghetti, Smoked Duck Breast, Sous Vide Egg, Spinach, Mushroom', 9.00, 'Pasta', 'https://images.deliveryhero.io/image/fd-sg/Products/5368047.jpg??width=800'),
(3, 1, 'Carbonara', 'Cream Sauce + Organic Spaghetti, Pork Bacon, Sous Vide Egg, Spinach, Button Mushroom', 11.80, 'Pasta', 'https://images.deliveryhero.io/image/fd-sg/Products/37909329.jpg??width=800'),
(4, 1, 'Chicken Alfredo', 'Cream Sauce + Organic Spaghetti, Chicken Thigh, Sous Vide Egg, Spinach, Button Mushroom', 11.80, 'Pasta', 'https://images.deliveryhero.io/image/fd-sg/Products/37909330.jpg??width=800'),
(5, 1, 'Meat Lovers', 'Cream Sauce + Organic Spaghetti, Smoked Duck, Pork Bacon, Chicken Thigh, Sous Vide Egg', 12.60, 'Pasta', 'https://images.deliveryhero.io/image/fd-sg/Products/37909336.jpg??width=800'),

-- Additional Inventory Table Data
(6, 2, 'Bibimbap Chicken', 'Popular Korean dish that combines rice, marinated chicken,egg, and an assortment of vegetables, all topped with a flavorful sauce', 6.75, 'Bibimbap', 'https://images.deliveryhero.io/image/fd-sg/Products/37336651.jpg??width=800'),
(7, 2, 'Japchae', 'Korean stir-fried glass noodles with vegetables, mushrooms, and marinated beef', 5.40, 'Starters', 'https://images.deliveryhero.io/image/fd-sg/Products/37336659.jpg??width=800'),
(8, 2, 'Bibimbap Pork', 'Popular Korean dish that combines rice, marinated pork,egg, and an assortment of vegetables, all topped with a flavorful sauce', 6.75, 'Bibimbap', 'https://images.deliveryhero.io/image/fd-sg/Products/37336653.jpg??width=800'),
(9, 2, 'Korean Pancake', 'Savory and crispy pancake made with a variety of vegetables and served with a dipping sauce', 6.75, 'Starters', 'https://images.deliveryhero.io/image/fd-sg/Products/37336655.jpg??width=800'),
(10, 2, 'Bibimbap Beef', 'Popular Korean dish that combines rice, marinated beef,egg, and an assortment of vegetables, all topped with a flavorful sauce', 6.75, 'Bibimbap', 'https://images.deliveryhero.io/image/fd-sg/Products/37336654.jpg??width=800'),

(11, 3, 'Kuro Fried Chicken', 'Juicy Chicken Tight Katsu', 6.75, 'Main', 'https://images.squarespace-cdn.com/content/v1/64a2a6571409001ff0ef5f8d/c537fe8b-2f2f-45fe-8e53-83ae89c46cbd/KURO_SOCIAL_IG_POST_CURRYMENU_WKF_24072023-02.png?format=1000w'),
(12, 3, 'Apple of my Ribeye', 'Australian Ribeye Shabu Shabu with a custom Gyu sauce that contains no apples', 7.00, 'Mains', 'https://images.squarespace-cdn.com/content/v1/64a2a6571409001ff0ef5f8d/a182c702-7743-463f-bfde-da01c4eb21fa/KURO_SOCIAL_IG_POST_DONMENU_WKF_24072023-04.png?format=1500w'),
(13, 3, 'Melty Beef', 'Black Angus Short Rib Curry cooked for 48hr till tender', 8.50, 'Mains', 'https://images.squarespace-cdn.com/content/v1/64a2a6571409001ff0ef5f8d/19091cc2-5931-4789-be42-a33be133b204/KURO_SOCIAL_IG_POST_CURRYMENU_WKF_24072023-03.png?format=1500w'),
(14, 3, 'Unami Tuna Belly', 'Marinated hand-chopped Tuna, seaweed & water turnip', 8.50, 'Starters', 'https://images.squarespace-cdn.com/content/v1/64a2a6571409001ff0ef5f8d/6e0d60a6-0a6b-4e6b-b38e-d7c1419bb5b0/Sides+IG-01.png?format=1500w'),
(15, 3, 'Seaweed Chicken', 'Homemade Wasabi Mayo ', 6.75, 'Starters', 'https://images.squarespace-cdn.com/content/v1/64a2a6571409001ff0ef5f8d/9562c49f-61d6-4416-9583-b9ac6ce9e8e6/Sides+IG-03.png?format=750w'),

(16, 4, 'Kaya Milk Bun', '', 2.20, 'Bun', 'https://eatbook.sg/wp-content/uploads/2022/12/khoon-coffeehouse-express-buns-stack.jpg'),
(17, 4, 'Lotus Biscoff Bun', '', 2.20, 'Bun', 'https://eatbook.sg/wp-content/uploads/2022/12/khoon-coffeehouse-express-biscoff-bun-1024x683.jpg'),
(18, 4, 'Honey Butter Bun', '', 2.20, 'Bun', 'https://eatbook.sg/wp-content/uploads/2022/12/khoon-coffeehouse-express-toasting-buns-1024x683.jpg'),
(19, 4, 'Peanut Butter Bun', '', 2.20, 'Bun', 'https://eatbook.sg/wp-content/uploads/2022/12/khoon-coffeehouse-express-toasting-buns-1024x683.jpg'),
(20, 4, 'Chocolate Bun', '', 2.20, 'Bun', 'https://eatbook.sg/wp-content/uploads/2022/12/khoon-coffeehouse-express-toasting-buns-1024x683.jpg'),

(21, 5, 'Mango Passion Pop Smoothie', '', 6.40, 'Premium Ice Blend', 'https://images.deliveryhero.io/image/fd-sg/Products/17797931.jpg??width=800'),
(22, 5, 'Brown Sugar Pearl Milk Tea', '', 5.50, 'Brown Sugar', 'https://images.deliveryhero.io/image/fd-sg/Products/17797894.jpg??width=800'),
(23, 5, 'Brown Sugar Boba Milk', '', 7.00, 'Brown Sugar', 'https://images.deliveryhero.io/image/fd-sg/Products/17797895.jpg??width=800'),
(24, 5, 'Three Gems', '', 6.00, 'Premium Milk Tea', 'https://images.deliveryhero.io/image/fd-sg/Products/17797909.jpg??width=800'),
(25, 5, 'American Milk Coffee', '', 5.50, 'Coffee', 'https://images.deliveryhero.io/image/fd-sg/Products/17797955.jpg??width=800');

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

-- Inventory Table Data
INSERT INTO Inventory (VendorID, ItemID, QuantityAvailable) VALUES 
(1, 1, 50), 
(1, 2, 30), 
(1, 3, 20), 
(1, 4, 25), 
(1, 5, 15), 

(2, 6, 40), 
(2, 7, 40), 
(2, 8, 60), 
(2, 9, 35), 
(2, 10, 50), 

(3, 11, 20), 
(3, 12, 20), 
(3, 13, 30),
(3, 14, 35), 
(3, 15, 50), 

(4, 16, 50), 
(4, 17, 30), 
(4, 18, 20), 
(4, 19, 25), 
(4, 20, 15), 

(5, 21, 20), 
(5, 22, 20), 
(5, 23, 30),
(5, 24, 35), 
(5, 25, 50);