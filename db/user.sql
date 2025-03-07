CREATE DATABASE IF NOT EXISTS user;
USE user;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample users
INSERT INTO users (name, email, password) VALUES 
('Alice Johnson', 'alice@example.com','dummy_pw'),
('Bob Smith', 'bob@example.com','testpw'),
('Charlie Brown', 'charlie@example.com', 'dummy_pw');