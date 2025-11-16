🏥 Pharmacy Stock and Sales Management System
A comprehensive desktop application for managing pharmacy operations with role-based access control (RBAC), built using Python Tkinter and MySQL.

📋 Overview
This Pharmacy Management System provides a complete solution for managing medicines, customers, orders, prescriptions, and employee operations with integrated privilege management and security features.

✨ Key Features
🔐 Role-Based Access Control (RBAC)

5 User Roles: Admin, Supervisor, Manager, Pharmacist, Cashier
Granular permissions for add, edit, delete operations
Salary visibility controls
Employee management restrictions

💊 Medicine Management

Track medicine inventory with batch numbers
Expiry date monitoring with automatic notifications
Stock quantity management
Supplier integration
Medicine disposal tracking

👥 Customer & Order Management

Customer registration 
Order processing and tracking
Prescription management with doctor records
Multi-drug prescriptions support

💰 Billing System

bill generation

📊 Advanced Reporting & Queries

Pre-built analytical queries (joins, aggregations, nested queries)
Custom SQL query execution
Stock valuation reports
Expiry tracking reports
Insurance and notification tracking

🔔 Notification System

Employee notification tracking (IS_NOTIFIED table)
Prescription alerts
Expiry warnings
Mark notifications as seen

🗄️ Database Features

MySQL stored procedures 
User-defined functions 
Triggers for stock updates
Foreign key constraints with proper relationships

🛠️ Technology Stack

Frontend: Python , Tkinter (ttk widgets)
Backend: MySQL 
Database Connector: mysql-connector-python
Design Pattern: MVC-inspired architecture

📦 Database Schema
Core Tables

EMPLOYEE - Staff management with authentication
CUSTOMER - Customer records with insurance
MEDICINE - Drug inventory with batch tracking
SUPPLIER - Supplier information
ORDER - Customer orders
ORDERED_DRUG - Order line items
BILL - Billing records
PRESCRIPTION - Medical prescriptions
PRESCRIBED_DRUG - Prescription details
DISPOSAL - Expired/damaged drug disposal
NOTIFICATION - System notifications

Feature          | Admin | Supervisor | Manager | Pharmacist | Cashier
-----------------|-------|------------|---------|------------|--------
All Tabs         |  YES  |    YES     |   NO    |     NO     |   NO
Can Add          |  YES  |    YES     |   YES   |    YES     |  YES
Can Edit         |  YES  |    YES     |   YES   |    YES     |   NO
Can Delete       |  YES  |    YES     |   YES   |     NO     |   NO
View Salary      |  YES  |    YES     |   YES   |     NO     |   NO
Manage Employees |  YES  |     NO     |   YES   |     NO     |   NO

🚀 Installation
Prerequisites
bash- Python 3.7+
- MySQL Server 8.0+
- pip package manager
Setup Steps

Clone the repository

bashgit clone https://github.com/yourusername/pharmacy-management-system.git
cd pharmacy-management-system

Install dependencies

bashpip install mysql-connector-python

Configure database


Update DB_CONFIG in the script with your MySQL credentials:

pythonDB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "PharmacyDB",
    "port": 3306
}

Import database schema

bashmysql -u root -p < database_schema.sql

Run the application

bashpython frontend_pharmacy_with_privileges.py
👤 Default Login Credentials
Admin Access:

Username: admin
Password: admin123

Automatic warnings for medicines expiring within 7 days
Expired medicine notifications on dashboard
Color-coded alerts

Stock Management

Real-time stock updates via triggers
Automatic stock deduction on orders
Total stock value calculation

Prescription Workflow

Create prescription with customer and doctor details
Add multiple drugs to prescription
Link prescription to orders
Automatic notification generation


👨‍💻 Author
B Neeharika (PES2UG23CS114)
Bhoomika H B (PES2UG23CS126)

Email: nhkb99@gmail.com
       bhoomi172021@gmail.com
       

🙏 Acknowledgments

Built as a database management project
Implements RBAC security patterns
Follows pharmacy industry best practices
