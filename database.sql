-- Student Record Management System - MySQL schema
-- Run in MySQL Workbench (the app also creates this automatically on first start).

CREATE DATABASE IF NOT EXISTS student_records;
USE student_records;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(10) NOT NULL,
    course VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    mark_1 DECIMAL(5,2) NOT NULL,   -- Python
    mark_2 DECIMAL(5,2) NOT NULL,   -- DBMS
    mark_3 DECIMAL(5,2) NOT NULL,   -- Mathematics
    mark_4 DECIMAL(5,2) NOT NULL,   -- Computer Networks
    mark_5 DECIMAL(5,2) NOT NULL,   -- Software Engineering
    created_at DATETIME NOT NULL
);

-- Optional sample data
INSERT IGNORE INTO students
(roll_no, name, email, phone, course, semester, mark_1, mark_2, mark_3, mark_4, mark_5, created_at)
VALUES
('MCA-001', 'Aarav Sharma', 'aarav.sharma@example.com', '9876543210', 'MCA', 2, 92, 88, 85, 90, 94, NOW()),
('MCA-002', 'Simran Kaur',  'simran.kaur@example.com',  '9876543211', 'MCA', 2, 76, 81, 69, 72, 78, NOW()),
('MCA-003', 'Rohan Verma',  'rohan.verma@example.com',  '9876543212', 'MCA', 2, 55, 48, 62, 51, 58, NOW()),
('MCA-004', 'Neha Gupta',   'neha.gupta@example.com',   '9876543213', 'MCA', 2, 38, 45, 52, 41, 47, NOW()),
('BCA-001', 'Karan Singh',  'karan.singh@example.com',  '9876543214', 'BCA', 4, 84, 79, 91, 87, 83, NOW());

-- Query used by the application
SELECT * FROM students ORDER BY roll_no;
