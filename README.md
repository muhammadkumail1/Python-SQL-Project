# Customer, Orders, and Shipping Management System

A comprehensive GUI application built with Python, Tkinter, and SQLite for managing customer data, orders, and shipping information. Provides an intuitive tabbed interface for all operations with proper data relationships and validation.

## Features

- **Customer Registration**: Add new customers with personal details and validation
- **Order Management**: Create orders linked to existing customers with product details
- **Shipping Tracking**: Add and track shipping information for orders
- **Customer Search**: Find customers by full name and view their complete order history
- **Data Views**: Comprehensive lists of all customers and all orders with shipping status
- **Data Integrity**: Foreign key constraints ensure proper relationships between tables
- **Dynamic Updates**: Refresh buttons to update dropdown lists with latest data

## Database Schema

The application uses SQLite with three main tables connected through foreign key relationships:

### customers
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique customer identifier
- `first_name` (TEXT NOT NULL) - Customer's first name
- `last_name` (TEXT NOT NULL) - Customer's last name
- `email` (TEXT NOT NULL UNIQUE) - Customer's email address (must be unique)
- `phone` (TEXT NOT NULL) - Customer's phone number
- `created_at` (TEXT NOT NULL) - Registration timestamp

### orders
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique order identifier
- `customer_id` (INTEGER NOT NULL) - References customers.id (foreign key)
- `product_name` (TEXT NOT NULL) - Name of the ordered product
- `quantity` (INTEGER NOT NULL) - Number of items ordered
- `price` (REAL NOT NULL) - Price per item
- `order_date` (TEXT NOT NULL) - Order placement timestamp

### shipping
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT) - Unique shipping record identifier
- `order_id` (INTEGER NOT NULL UNIQUE) - References orders.id (foreign key)
- `address` (TEXT NOT NULL) - Shipping street address
- `city` (TEXT NOT NULL) - Shipping city
- `postal_code` (TEXT NOT NULL) - Shipping postal/ZIP code
- `country` (TEXT NOT NULL) - Shipping country
- `status` (TEXT NOT NULL) - Shipping status (e.g., Processing, Shipped, Delivered)
- `shipped_date` (TEXT) - Shipment timestamp (set automatically when status is "Shipped" or "Delivered")

### Relationships
- **One-to-Many**: One customer can have multiple orders (customers.id → orders.customer_id)
- **One-to-One**: Each order can have at most one shipping record (orders.id → shipping.order_id)
- **Foreign Key Enforcement**: SQLite foreign keys are enabled to maintain referential integrity

## Requirements

- Python 3.8 or newer
- Tkinter (included with Python standard library)
- SQLite3 (included with Python standard library)

## Usage

1. Open a terminal/command prompt in the project directory
2. Run the application:

```bash
python customer_orders.py
```

3. The GUI window will open with multiple tabs:

### Register Tab
- Enter customer details (first name, last name, email, phone)
- Click "Register Customer" to add to database
- Email must be unique across all customers

### Orders Tab
- Select a customer from the dropdown (use "Refresh Customers" if needed)
- Enter product name, quantity, and price per item
- Click "Add Order" to create a new order linked to the selected customer

### Shipping Tab
- Select an order from the dropdown (use "Refresh Orders" if needed)
- Enter shipping address details and status
- Click "Add Shipping" to attach shipping information to the order
- Shipped date is set automatically for "Shipped" or "Delivered" status

### Search Tab
- Enter customer's full name (first and last name)
- Click "Search" to view customer details and all their orders with shipping status

### Customers Tab
- Click "Refresh Customers" to view a list of all registered customers

### All Orders Tab
- Click "Refresh All Orders" to view every order in the system with customer names and shipping details

## Files

- `customer_orders.py` - Main application file containing all logic and GUI
- `customer_orders.db` - SQLite database file (created automatically on first run)

## Sample Workflow

1. **Register a Customer**:
   - Go to Register tab
   - Enter: First name "Muhammad", Last name "Kumail", Email "kumail@gmail.com", Phone "12345566"
   - Click Register

2. **Add an Order**:
   - Go to Orders tab
   - Select "1: Muhammad Kumail (kumail@example.com)" from customer dropdown
   - Enter: Product "Laptop", Quantity "1", Price "1200.00"
   - Click Add Order

3. **Add Shipping**:
   - Go to Shipping tab
   - Select "Order 1: Laptop (Muhammad Kumail)" from order dropdown
   - Enter address details and set status to "Shipped"
   - Click Add Shipping

4. **Search Customer**:
   - Go to Search tab
   - Enter "Muhammad Kumail"
   - Click Search to see customer info, order details, and shipping status

## Notes

- The database file `customer_orders.db` is created automatically in the same directory as the script
- All tables are created with proper constraints on first run
- Foreign key relationships prevent orphaned records
- Input validation ensures data quality
- Refresh buttons update dropdown lists to reflect recent changes
- Shipping records are unique per order (one shipping entry per order)
- Timestamps use ISO format for consistency

## Data Integrity

The application enforces data integrity through:
- Required fields (NOT NULL constraints)
- Unique email addresses
- Foreign key relationships
- Input validation in the GUI
- Automatic timestamp generation

This ensures a robust and reliable customer management system.
