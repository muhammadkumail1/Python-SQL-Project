# Customer, Orders, and Shipping Management System

A simple Python + SQLite console application for managing customers, orders, and shipping details.

## Files

- `customer_orders.py` - main program file
- `customer_orders.db` - SQLite database file (created automatically when running the program)

## Requirements

- Python 3.8 or newer

## Run the program

1. Open a terminal in the project folder.
2. Run:

```bash
python customer_orders.py
```

3. A graphical user interface will open.
4. Use the tabs to:

- Register new customers
- Insert customer orders
- Add shipping details
- Search by customer full name

## Sample usage

```
Customer, Orders, and Shipping Management System

Select an option:
1. Register new customer
2. Insert customer order
3. Add shipping details
4. Search customer by full name
5. List registered customers
6. Exit
Option: 1

=== Register New Customer ===
First name: Alice
Last name: Johnson
Email: alice@example.com
Phone number: 555-0199
Customer registered successfully.

Select an option:
Option: 2

=== Add Customer Order ===
Customer ID: 1
Product name: Laptop
Quantity: 2
Price per item: 1200
Order inserted successfully.

Select an option:
Option: 3

=== Add Shipping Details ===
Order ID: 1
Shipping address: 123 Main St
City: Springfield
Postal code: 12345
Country: USA
Status (e.g. Processing, Shipped, Delivered): Shipped
Shipping details added successfully.

Select an option:
Option: 4

=== Search Customer Orders ===
Enter customer full name: Alice Johnson

Customer: Alice Johnson
Email: alice@example.com
Phone: 555-0199
Registered: 2026-04-05T14:30:00

Orders:

Order ID: 1
Product: Laptop
Quantity: 2
Price per item: 1200.00
Total amount: 2400.00
Order date: 2026-04-05T14:31:00
Shipping:
  Address: 123 Main St
  City: Springfield
  Postal code: 12345
  Country: USA
  Status: Shipped
  Shipped date: 2026-04-05T14:32:00
```

## Features

- **Register Customers**: Add new customers with personal details.
- **Add Orders**: Select an existing customer from a dropdown and add order details. Use "Refresh Customers" to update the list.
- **Add Shipping**: Select an existing order from a dropdown and add shipping information. Use "Refresh Orders" to update the list.
- **Search Customers**: Find customers by full name and view their orders and shipping status.
- **List Customers**: View all registered customers.
- **View All Orders**: Display all orders with customer details and shipping status. Use "Refresh All Orders" to update.

## Database Schema

- **customers**: id, first_name, last_name, email, phone, created_at
- **orders**: id, customer_id (FK to customers), product_name, quantity, price, order_date
- **shipping**: id, order_id (FK to orders), address, city, postal_code, country, status, shipped_date

Foreign key constraints ensure data integrity.
