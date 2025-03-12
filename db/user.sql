-- Drop the database if it exists and create a new one
DROP DATABASE IF EXISTS user;
CREATE DATABASE user;
USE user;

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert additional sample users
INSERT INTO users (name, email, password) VALUES 
('David Wilson', 'david@example.com', 'password123'),
('Eva Green', 'eva@example.com', 'qwerty123'),
('Frank White', 'frank@example.com', 'hello1234'),
('Grace Lee', 'grace@example.com', 'welcome2023'),
('Hannah King', 'hannah@example.com', 'mypassword'),
('Ian Walker', 'ian@example.com', 'testpassword'),
('Jack Brown', 'jack@example.com', 'jackpassword');
