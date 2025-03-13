DROP DATABASE IF EXISTS user;
CREATE DATABASE IF NOT EXISTS user;
USE user;

CREATE TABLE IF NOT EXISTS users (  id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email, password) VALUES 
('Alice Johnson', 'alice.johnson@example.com', 'Alice@2024!'),
('Bob Smith', 'bob.smith@example.com', 'BobSecure#99'),
('Charlie Brown', 'charlie.brown@example.com', 'Ch@rliePass123'),
('David Williams', 'david.williams@example.com', 'D@vid456!'),
('Emma Davis', 'emma.davis@example.com', 'EmmaStrongPass#1'),
('Frank Miller', 'frank.miller@example.com', 'Frank_Mill99'),
('Grace Lee', 'grace.lee@example.com', 'Gr@ceLee2024'),
('Henry Wilson', 'henry.wilson@example.com', 'Henry_Wilson$45'),
('Isabella Martinez', 'isabella.martinez@example.com', 'IsabellaP@ssword'),
('Jack Taylor', 'jack.taylor@example.com', 'JackTay!lor89'),
('Karen White', 'karen.white@example.com', 'Karen#White2023'),
('Leo Harris', 'leo.harris@example.com', 'LeoH@rrisXyz'),
('Mia Clark', 'mia.clark@example.com', 'MiaC!arkSecure');
