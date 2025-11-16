-- =======================
-- DATABASE CREATION
-- =======================
DROP DATABASE IF EXISTS PharmacyDB;
CREATE DATABASE PharmacyDB;
USE PharmacyDB;

-- =======================
-- EMPLOYEE RELATED TABLES
-- =======================
CREATE TABLE EMPLOYEE (
    EmpID varchar(5) PRIMARY KEY,
    Ename VARCHAR(50) NOT NULL,
    DOB DATE,
    Role VARCHAR(30),
    Salary DECIMAL(10,2),
    Phone VARCHAR(15),
    AuthKey VARCHAR(30)
);

CREATE TABLE EMPLOYEE_PHONE (
    EmpID VARCHAR(5),
    Phone VARCHAR(15),
    PRIMARY KEY (EmpID, Phone),
    FOREIGN KEY (EmpID) REFERENCES EMPLOYEE(EmpID)
);

CREATE TABLE NOTIFICATION (
    NID varchar(5) PRIMARY KEY,
    Type VARCHAR(20),
    Message VARCHAR(255)
);

CREATE TABLE IS_NOTIFIED (
    EmpID varchar(5),
    NID varchar(5),
    PRIMARY KEY (EmpID, NID),
    FOREIGN KEY (EmpID) REFERENCES EMPLOYEE(EmpID),
    FOREIGN KEY (NID) REFERENCES NOTIFICATION(NID)
);

-- =======================
-- SUPPLIER RELATED TABLES
-- =======================
CREATE TABLE SUPPLIER (
    SupID varchar(5) PRIMARY KEY,
    SupName VARCHAR(50) NOT NULL,
    License_no VARCHAR(30) UNIQUE,
    Email VARCHAR(50),
    Phone VARCHAR(15),
    Street VARCHAR(50),
    City VARCHAR(30)
);

CREATE TABLE SUPPLIER_PHONE (
    SupID varchar(5),
    Phone VARCHAR(15),
    PRIMARY KEY (SupID, Phone),
    FOREIGN KEY (SupID) REFERENCES SUPPLIER(SupID)
);

-- =======================
-- MEDICINE TABLE
-- =======================
CREATE TABLE MEDICINE (
    BatchNo VARCHAR(20),
    DrugName VARCHAR(50),
    ExpiryDate DATE,
    Stock_quantity INT,
    Price DECIMAL(10,2),
    SupID varchar(5),
    Type VARCHAR(30),
    PRIMARY KEY (BatchNo, DrugName),
    FOREIGN KEY (SupID) REFERENCES SUPPLIER(SupID)
);

-- =======================
-- SUPPLIES_TO TABLE
-- =======================
CREATE TABLE SUPPLIES_TO (
    SupID VARCHAR(5),
    DrugName VARCHAR(50),
    BatchNo VARCHAR(20),
    PRIMARY KEY (SupID, DrugName, BatchNo),
    FOREIGN KEY (SupID) REFERENCES SUPPLIER(SupID),
    FOREIGN KEY (BatchNo, DrugName) REFERENCES MEDICINE(BatchNo, DrugName)
);

-- =======================
-- INSURANCE & CUSTOMER
-- =======================
CREATE TABLE INSURANCE (
    InsuranceID VARCHAR(5) PRIMARY KEY,
    StartDate DATE,
    EndDate DATE,
    CompName VARCHAR(50)
);

CREATE TABLE CUSTOMER (
    Cid VARCHAR(5) PRIMARY KEY,
    Cname VARCHAR(50) NOT NULL,
    DOB DATE,
    InsuranceID VARCHAR(5),
    Street VARCHAR(50),
    DNO VARCHAR(10),
    City VARCHAR(30),
    Phone VARCHAR(15),
    FOREIGN KEY (InsuranceID) REFERENCES INSURANCE(InsuranceID)
);

CREATE TABLE CUSTOMER_PHONE (
    Cid VARCHAR(5),
    Phone VARCHAR(15),
    PRIMARY KEY (Cid, Phone),
    FOREIGN KEY (Cid) REFERENCES CUSTOMER(Cid)
);

-- =======================
-- ORDER & PRESCRIPTIONS
-- =======================
CREATE TABLE `ORDER` (
    OrderID varchar(5) PRIMARY KEY,
    Cid VARCHAR(5),
    EmpID VARCHAR(5),
    OrderDate DATE,
    FOREIGN KEY (Cid) REFERENCES CUSTOMER(Cid),
    FOREIGN KEY (EmpID) REFERENCES EMPLOYEE(EmpID)
);

CREATE TABLE PRESCRIPTION (
    PresID VARCHAR(5) PRIMARY KEY,
    Cid VARCHAR(5),
    DocID INT,
    PresDate DATE,
    OrderID VARCHAR(5),
    FOREIGN KEY (Cid) REFERENCES CUSTOMER(Cid),
    FOREIGN KEY (OrderID) REFERENCES `ORDER`(OrderID)
);

CREATE TABLE PRESCRIBED_DRUG (
    DrugID VARCHAR(5),
    PresID VARCHAR(5),
    Quantity INT,
    PRIMARY KEY (DrugID, PresID),
    FOREIGN KEY (PresID) REFERENCES PRESCRIPTION(PresID)
);

CREATE TABLE ORDERED_DRUG (
    DrugName VARCHAR(50),
    OrderID VARCHAR(5),
    BatchNo VARCHAR(20),
    Ordered_quantity INT,
    Price DECIMAL(10,2),
    PRIMARY KEY (DrugName, OrderID, BatchNo),
    FOREIGN KEY (OrderID) REFERENCES `ORDER`(OrderID),
    FOREIGN KEY (BatchNo, DrugName) REFERENCES MEDICINE(BatchNo, DrugName)
);

-- =======================
-- BILL & DISPOSAL
-- =======================
CREATE TABLE BILL (
    BillID INT PRIMARY KEY,
    Cid VARCHAR(5),
    OrderID VARCHAR(5),
    Total_amt DECIMAL(10,2),
    Custpay DECIMAL(10,2),
    Inspay DECIMAL(10,2),
    FOREIGN KEY (Cid) REFERENCES CUSTOMER(Cid),
    FOREIGN KEY (OrderID) REFERENCES `ORDER`(OrderID)
);

CREATE TABLE DISPOSAL (
    BatchNo VARCHAR(20),
    DrugName VARCHAR(50),
    Dis_Qty INT,
    Company VARCHAR(50),
    Emp_ID VARCHAR(5),
    Expired BOOLEAN,
    Damaged BOOLEAN,
    Trial_Batch BOOLEAN,
    Contaminated BOOLEAN,
    PRIMARY KEY (BatchNo, DrugName),
    FOREIGN KEY (BatchNo, DrugName) REFERENCES MEDICINE(BatchNo, DrugName),
    FOREIGN KEY (Emp_ID) REFERENCES EMPLOYEE(EmpID)
);

-- =======================
-- SAMPLE DATA
-- =======================
INSERT INTO EMPLOYEE VALUES 
('E1', 'Alice', '1990-05-12', 'Pharmacist', 45000, '9876543210', 'AUTH123'),
('E2', 'Bob', '1985-09-20', 'Manager', 60000, '9876501234', 'AUTH456');

INSERT INTO NOTIFICATION VALUES
('N1', 'Expiry Alert', 'Batch B001 expiring soon'),
('N2', 'Stock Alert', 'Amoxicillin stock running low');

INSERT INTO IS_NOTIFIED VALUES ('E1', 'N1'),('E2', 'N2');

INSERT INTO SUPPLIER VALUES
('S1', 'MediSupplies', 'LIC123', 'medisup@gmail.com', '8888888888', 'MG Road', 'Bangalore'),
('S2', 'PharmaCare', 'LIC456', 'phcare@gmail.com', '9999999999', 'BTM Layout', 'Bangalore');

INSERT INTO MEDICINE VALUES 
('B001', 'Paracetamol', '2026-05-01', 200, 2.50, 'S1', 'Tablet'),
('B002', 'Amoxicillin', '2025-12-01', 150, 5.00, 'S2', 'Capsule'),
('B003', 'DOLO', '2027-12-31', 200, 2.50, 'S1', 'Tablet');
INSERT INTO MEDICINE (BatchNo, DrugName, Stock_quantity, Expirydate, Price)
VALUES ('B004', 'Aspirin', 100, '2026-12-31', 7.00);
INSERT INTO MEDICINE VALUES 
('B006', 'Calamine', '2026-05-01', 100, 2.50, 'S1', 'Syrup');
INSERT INTO MEDICINE VALUES 
('B009', 'C-33', '2024-05-01', 100, 2.50, 'S1', 'Tablet');
INSERT INTO MEDICINE VALUES 
('B010', 'cofsil', '2024-05-01', 100, 2.50, 'S1', 'Tablet');


INSERT INTO SUPPLIES_TO VALUES
('S1', 'Paracetamol', 'B001'),
('S2', 'Amoxicillin', 'B002');


INSERT INTO INSURANCE VALUES
('I1', '2024-01-01', '2025-01-01', 'HealthFirst'),
('I2', '2024-06-01', '2025-06-01', 'MediSecure');
INSERT INTO INSURANCE VALUES
('I3', '2024-07-01', '2025-07-01', 'HappyHealth');


INSERT INTO CUSTOMER VALUES
('C1', 'Rahul', '1995-03-15', 'I1', 'Jayanagar', '12A', 'Bangalore', '9123456780'),
('C2', 'Sneha', '1998-07-22', 'I2', 'Indiranagar', '56B', 'Bangalore', '9234567890');
INSERT INTO CUSTOMER VALUES
('C3', 'Riya', '1995-03-15', 'I3', 'Jayanagar', '12B', 'Bangalore', '9123666780');


INSERT INTO `ORDER` VALUES 
('O1', 'C1', 'E1', '2025-09-02'),
('O2', 'C2', 'E2', '2025-09-06'),
('O3', 'C1', 'E1', '2025-10-27');
INSERT INTO `ORDER` (OrderID, Cid, EmpID, OrderDate)
VALUES ('O4', 'C2', 'E1', '2025-10-28');
INSERT INTO `ORDER` (OrderID, Cid, EmpID, OrderDate)
VALUES ('O5', 'C2', 'E1', '2025-10-28');
INSERT INTO `ORDER` (OrderID, Cid, EmpID, OrderDate)
VALUES ('O6', 'C2', 'E1', '2025-10-28');
INSERT INTO `ORDER` (OrderID, Cid, EmpID, OrderDate)
VALUES ('O7', 'C1', 'E1', '2025-10-28');
INSERT INTO `ORDER` (OrderID, Cid, EmpID, OrderDate)
VALUES ('O8', 'C1', 'E1', '2025-10-30');
INSERT INTO `ORDER` (OrderID, Cid, EmpID, OrderDate)
VALUES ('10', 'C1', 'E1', '2025-10-30');




INSERT INTO PRESCRIPTION VALUES
('P1', 'C1', 101, '2025-09-01', 'O1'),
('P2', 'C2', 102, '2025-09-05', 'O2');

INSERT INTO PRESCRIBED_DRUG VALUES
('D1', 'P1', 10),
('D2', 'P2', 5);

INSERT INTO ORDERED_DRUG VALUES
('Paracetamol', 'O1', 'B001', 10, 25.00),
('DOLO', 'O2', 'B003', 10, 25.00),
('Paracetamol', 'O3', 'B001', 10, 25.00);

INSERT INTO BILL VALUES
(1, 'C1', 'O1', 25.00, 10.00, 15.00);
INSERT INTO BILL VALUES
(2, 'C2', 'O2', 25.00, 5.00, 20.00);

INSERT INTO DISPOSAL VALUES
('B001', 'Paracetamol', 50, 'WasteCo', 'E1', TRUE, FALSE, FALSE, TRUE),
('B002', 'Amoxicillin', 30, 'BioDispose', 'E2', FALSE, TRUE, TRUE, FALSE);

-- =======================
-- TRIGGERS
-- =======================
DELIMITER $$

-- 1. Reduce stock after sale
CREATE TRIGGER trg_reduce_stock
AFTER INSERT ON ORDERED_DRUG
FOR EACH ROW
BEGIN
    UPDATE MEDICINE
    SET Stock_quantity = Stock_quantity - NEW.Ordered_quantity
    WHERE BatchNo = NEW.BatchNo AND DrugName = NEW.DrugName;
END $$

-- INSERT INTO ORDERED_DRUG VALUES ('Amoxicillin', 'O5', 'B002', 5, 25.00);
-- SELECT * FROM ORDERED_DRUG;

-- 2. Prevent sale if stock insufficient
CREATE TRIGGER trg_check_stock_before_order
BEFORE INSERT ON ORDERED_DRUG
FOR EACH ROW
BEGIN
    DECLARE current_stock INT;
    SELECT Stock_quantity INTO current_stock
    FROM MEDICINE
    WHERE BatchNo = NEW.BatchNo AND DrugName = NEW.DrugName;
    IF current_stock < NEW.Ordered_quantity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Not enough stock to process the order.';
    END IF;
END $$

-- 3. Block expired medicines from sale
CREATE TRIGGER trg_block_expired
BEFORE INSERT ON ORDERED_DRUG
FOR EACH ROW
BEGIN
    DECLARE exp DATE;
    SELECT ExpiryDate INTO exp
    FROM MEDICINE
    WHERE BatchNo = NEW.BatchNo AND DrugName = NEW.DrugName;
    IF exp < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot sell expired medicine.';
    END IF;
END $$

DELIMITER ;

-- =======================
-- FUNCTIONS
-- =======================
DELIMITER $$

-- Function 1: Total stock value
CREATE FUNCTION TotalStockValue() 
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);
    SELECT SUM(Stock_quantity * Price) INTO total FROM MEDICINE;
    RETURN total;
END $$

-- Function 2: Check if medicine expired
CREATE FUNCTION IsExpired(p_batch VARCHAR(20), p_name VARCHAR(50)) 
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE exp DATE;
    SELECT ExpiryDate INTO exp 
    FROM MEDICINE 
    WHERE BatchNo = p_batch AND DrugName = p_name;
    RETURN exp < CURDATE();
END $$

DELIMITER ;

-- =======================
-- PROCEDURES
-- =======================
DELIMITER $$

-- Procedure 1: Add new medicine

CREATE PROCEDURE AddMedicine(
    IN p_batch VARCHAR(20), IN p_name VARCHAR(50),
    IN p_exp DATE, IN p_stock INT,
    IN p_price DECIMAL(10,2), IN p_supID VARCHAR(5), IN p_type VARCHAR(30)
)
BEGIN
    INSERT INTO MEDICINE VALUES (p_batch, p_name, p_exp, p_stock, p_price, p_supID, p_type);
END $$


-- Procedure 2: Create new order

CREATE PROCEDURE CreateOrder(
    IN p_orderID varchar(5), IN p_cid varchar(5), IN p_empID varchar(5), IN p_date DATE
)
BEGIN
    INSERT INTO `ORDER` VALUES (p_orderID, p_cid, p_empID, p_date);
END $$

-- Procedure 3: Generate Bill

DELIMITER $$

DROP PROCEDURE IF EXISTS GenerateBill;

CREATE PROCEDURE GenerateBill(
    IN p_billID INT,
    IN p_cid VARCHAR(5),
    IN p_orderID VARCHAR(5)
)
BEGIN
    DECLARE total DECIMAL(10,2);
    
    SELECT SUM(Ordered_quantity * Price)
    INTO total
    FROM ORDERED_DRUG
    WHERE OrderID = p_orderID;
    
    INSERT INTO BILL
    VALUES (p_billID, p_cid, p_orderID, total, total, 0);
END $$

DELIMITER ;


-- Demonstration / Presentation Queries
-- 1. Show all databases
SHOW DATABASES;

-- 2. Use PharmacyDB
USE PharmacyDB;

-- 3. Show all tables
SHOW TABLES;

-- 4. Describe table structures
DESCRIBE EMPLOYEE;
DESCRIBE SUPPLIER;
DESCRIBE MEDICINE;
DESCRIBE CUSTOMER;
DESCRIBE `ORDER`;
DESCRIBE PRESCRIPTION;
DESCRIBE ORDERED_DRUG;
DESCRIBE BILL;
DESCRIBE DISPOSAL;

-- 5. Select sample data from tables
SELECT * FROM EMPLOYEE;
SELECT * FROM SUPPLIER;
SELECT * FROM MEDICINE;
SELECT * FROM CUSTOMER;
SELECT * FROM `ORDER`;
SELECT * FROM PRESCRIPTION;
SELECT * FROM ORDERED_DRUG;
SELECT * FROM BILL;
SELECT * FROM DISPOSAL;
SELECT * FROM INSURANCE;



-- Show triggers, procedures & functions 

SHOW CREATE TRIGGER trg_reduce_stock;
SHOW CREATE TRIGGER trg_check_stock_before_order;
SHOW CREATE TRIGGER trg_block_expired;

SHOW CREATE PROCEDURE GenerateBill;
SHOW CREATE PROCEDURE AddMedicine;
SHOW CREATE PROCEDURE CreateOrder;

SHOW CREATE FUNCTION TotalStockValue;
SHOW CREATE FUNCTION IsExpired;

SHOW PROCEDURE STATUS WHERE Db = 'PharmacyDB';
SHOW FUNCTION STATUS WHERE Db = 'PharmacyDB';
SHOW TRIGGERS FROM PharmacyDB;

-- 1) Check current stock for a medicine
SELECT Stock_quantity FROM MEDICINE WHERE BatchNo = 'B001' AND DrugName = 'Paracetamol';


-- 2) Insert an ordered drug 
INSERT INTO ORDERED_DRUG (DrugName, OrderID, BatchNo, Ordered_quantity, Price)
VALUES ('Aspirin', 'O2', 'B002', 5, 2.50);

SELECT * FROM MEDICINE WHERE BatchNo = 'B004' AND DrugName = 'Aspirin';
SELECT * FROM MEDICINE WHERE BatchNo = 'B009' AND DrugName = 'C-33';
SELECT * FROM MEDICINE;

INSERT INTO ORDERED_DRUG (DrugName, OrderID, BatchNo, Ordered_quantity, Price)
VALUES ('Amoxicillin', 'O8', 'B002', 5, 5.00);
INSERT INTO ORDERED_DRUG (DrugName, OrderID, BatchNo, Ordered_quantity, Price)
VALUES ('cofsil', 'O5', 'B010', 4, 5.00);

-- 3) Show medicine stock after above insertion
SELECT Stock_quantity FROM MEDICINE WHERE BatchNo = 'B002' AND DrugName = 'Amoxicillin';
SELECT Stock_quantity FROM MEDICINE WHERE BatchNo = 'B003' AND DrugName = 'DOLO';



-- Demonstration of Procedures & Functions


-- 1) Calling AddMedicine to add a new batch
CALL AddMedicine('B005', 'Cetirizine', '2027-02-01', 180, 3.50, 'S1', 'Tablet');
CALL AddMedicine('B008', 'Cough Syrup', '2026-11-10', 80, 7.50, 'S2', 'Syrup');
CALL AddMedicine('B007', 'RELENT', '2026-11-10', 80, 7.50, 'S2', 'Syrup');


-- Confirm new medicine exists
SELECT * FROM MEDICINE WHERE BatchNo = 'B003' AND DrugName = 'Cetirizine';
SELECT * FROM MEDICINE WHERE BatchNo = 'B008' AND DrugName = 'Cough Syrup';
SELECT * FROM MEDICINE WHERE BatchNo = 'B007' AND DrugName = 'RELENT';
SELECT * FROM MEDICINE;

-- 2) Create a new order using CreateOrder
CALL CreateOrder('O6', 'C2', 'E1', '2025-10-20');
CALL CreateOrder('O7', 'C1', 'E2', '2025-10-20');
CALL CreateOrder('O9', 'C2', 'E1', '2025-10-20');
CALL CreateOrder('O10', 'C2', 'E1', '2025-10-20');


-- Confirm order row
SELECT * FROM `ORDER` WHERE OrderID = 'O8';
SELECT * FROM `ORDER`;


-- 3) Insert ordered drug for that order
INSERT INTO ORDERED_DRUG VALUES ('Aspirin', 'O4', 'B004', 2, 7.00);
INSERT INTO ORDERED_DRUG VALUES ('Calamine', '10', 'B006', 2, 7.00);


-- Show stock after the order
SELECT BatchNo, DrugName, Stock_quantity FROM MEDICINE WHERE BatchNo = 'B004';

-- 4) Generate bill for order
CALL GenerateBill(3, 'C2', 'O4');
CALL GenerateBill(4, 'C1', 'O1');

SELECT * FROM BILL;
SELECT * FROM `ORDER`;

-- Show the generated bill
SELECT * FROM BILL WHERE BillID = 3;

-- 5)To show total value of current stock
SELECT TotalStockValue() AS Total_Stock_Value;

-- 6) Check if a batch is expired using function IsExpired
SELECT IsExpired('B002', 'Amoxicillin') AS B002_Amoxicillin_Expired;
SELECT IsExpired('B010', 'cofsil') AS B002_Amoxicillin_Expired;


SHOW CREATE PROCEDURE CreateOrder;


SHOW PROCEDURE STATUS WHERE Db = 'PharmacyDB';
SHOW FUNCTION STATUS WHERE Db = 'PharmacyDB';
SHOW CREATE FUNCTION IsExpired;
SHOW CREATE FUNCTION TotalStockValue;

-- End