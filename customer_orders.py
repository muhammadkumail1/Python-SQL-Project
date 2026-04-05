import sqlite3
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

DB_FILENAME = Path(__file__).with_name("customer_orders.db")


def get_connection():
    """Establish and return a connection to the SQLite database."""
    return sqlite3.connect(DB_FILENAME)


def initialize_db():
    """Initialize the database by creating tables and enabling foreign keys."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                order_date TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS shipping (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL UNIQUE,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                postal_code TEXT NOT NULL,
                country TEXT NOT NULL,
                status TEXT NOT NULL,
                shipped_date TEXT,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
            """
        )
        conn.commit()


def register_customer(first_name, last_name, email, phone):
    """Register a new customer in the database."""
    created_at = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO customers (first_name, last_name, email, phone, created_at) VALUES (?, ?, ?, ?, ?)",
                (first_name, last_name, email, phone, created_at),
            )
            conn.commit()
            return True, "Customer registered successfully."
        except sqlite3.IntegrityError:
            return False, "A customer with that email already exists. Use a different email."


def insert_order(customer_id, product_name, quantity, price):
    """Insert a new order for a customer."""
    order_date = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
        if cursor.fetchone() is None:
            return False, "Customer ID not found. Please register the customer first."

        cursor.execute(
            "INSERT INTO orders (customer_id, product_name, quantity, price, order_date) VALUES (?, ?, ?, ?, ?)",
            (customer_id, product_name, quantity, price, order_date),
        )
        conn.commit()
        return True, "Order inserted successfully."


def add_shipping_details(order_id, address, city, postal_code, country, status):
    """Add shipping details for an order."""
    shipped_date = None
    if status.lower() in {"shipped", "delivered"}:
        shipped_date = datetime.now().isoformat(timespec="seconds")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM orders WHERE id = ?", (order_id,))
        if cursor.fetchone() is None:
            return False, "Order ID not found. Please add a valid order first."

        try:
            cursor.execute(
                "INSERT INTO shipping (order_id, address, city, postal_code, country, status, shipped_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (order_id, address, city, postal_code, country, status, shipped_date),
            )
            conn.commit()
            return True, "Shipping details added successfully."
        except sqlite3.IntegrityError:
            return False, "Shipping details already exist for this order. Update the shipping status if needed."


def search_customer(full_name):
    """Search for a customer by full name and return their details and orders."""
    full_name_normalized = full_name.strip().lower()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, first_name, last_name, email, phone, created_at FROM customers WHERE lower(first_name || ' ' || last_name) = ?",
            (full_name_normalized,),
        )
        customer = cursor.fetchone()
        if customer is None:
            return False, "Customer not found.", None

        customer_id, first_name, last_name, email, phone, created_at = customer
        cursor.execute(
            "SELECT id, product_name, quantity, price, order_date FROM orders WHERE customer_id = ? ORDER BY order_date",
            (customer_id,),
        )
        orders = cursor.fetchall()
        return True, {
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "created_at": created_at,
            "orders": orders,
        }, None


def get_shipping_for_order(order_id):
    """Retrieve shipping details for a specific order."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT address, city, postal_code, country, status, shipped_date FROM shipping WHERE order_id = ?",
            (order_id,),
        )
        return cursor.fetchone()


def list_customers_data():
    """Retrieve all customers from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, email FROM customers ORDER BY id")
        return cursor.fetchall()


def get_customers_for_combobox():
    """Get a list of customers formatted for the combobox."""
    customers = list_customers_data()
    return [f"{cid}: {fname} {lname} ({email})" for cid, fname, lname, email in customers]


def get_orders_for_combobox():
    """Get a list of orders formatted for the combobox."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.product_name, c.first_name, c.last_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY o.id
        """)
        orders = cursor.fetchall()
        return [f"Order {oid}: {product} ({fname} {lname})" for oid, product, fname, lname in orders]


def get_all_orders_data():
    """Retrieve all orders with customer details."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT o.id, o.product_name, o.quantity, o.price, o.order_date, c.first_name, c.last_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY o.id
        """)
        return cursor.fetchall()


def clear_fields(*vars_and_widgets):
    """Clear the specified StringVars and Text widgets."""
    for item in vars_and_widgets:
        if isinstance(item, tk.StringVar):
            item.set("")
        elif isinstance(item, tk.Text):
            item.delete("1.0", tk.END)


def register_customer_gui(first_name_var, last_name_var, email_var, phone_var, status_label):
    """Handle customer registration from the GUI."""
    first_name = first_name_var.get().strip()
    last_name = last_name_var.get().strip()
    email = email_var.get().strip()
    phone = phone_var.get().strip()

    if not (first_name and last_name and email and phone):
        messagebox.showwarning("Missing fields", "All customer fields are required.")
        return

    success, message = register_customer(first_name, last_name, email, phone)
    status_label.config(text=message)
    if success:
        clear_fields(first_name_var, last_name_var, email_var, phone_var)


def insert_order_gui(customer_combo_var, product_name_var, quantity_var, price_var, status_label):
    """Handle order insertion from the GUI."""
    selected = customer_combo_var.get()
    if not selected:
        messagebox.showwarning("Missing selection", "Please select a customer.")
        return

    try:
        customer_id = int(selected.split(":")[0])
    except ValueError:
        messagebox.showwarning("Invalid selection", "Invalid customer selected.")
        return

    try:
        quantity = int(quantity_var.get().strip())
        price = float(price_var.get().strip())
        if quantity < 1 or price < 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Invalid input", "Please enter valid numeric values for quantity and price.")
        return

    product_name = product_name_var.get().strip()
    if not product_name:
        messagebox.showwarning("Missing fields", "Product name is required.")
        return

    success, message = insert_order(customer_id, product_name, quantity, price)
    status_label.config(text=message)
    if success:
        clear_fields(customer_combo_var, product_name_var, quantity_var, price_var)


def add_shipping_gui(order_combo_var, address_var, city_var, postal_code_var, country_var, status_var, status_label):
    """Handle shipping details addition from the GUI."""
    selected = order_combo_var.get()
    if not selected:
        messagebox.showwarning("Missing selection", "Please select an order.")
        return

    try:
        order_id = int(selected.split(":")[0].split()[1])
    except (ValueError, IndexError):
        messagebox.showwarning("Invalid selection", "Invalid order selected.")
        return

    address = address_var.get().strip()
    city = city_var.get().strip()
    postal_code = postal_code_var.get().strip()
    country = country_var.get().strip()
    status_value = status_var.get().strip()

    if not (address and city and postal_code and country and status_value):
        messagebox.showwarning("Missing fields", "All shipping fields are required.")
        return

    success, message = add_shipping_details(order_id, address, city, postal_code, country, status_value)
    status_label.config(text=message)
    if success:
        clear_fields(order_combo_var, address_var, city_var, postal_code_var, country_var, status_var)


def search_customer_gui(full_name_var, output_text, status_label):
    """Handle customer search from the GUI."""
    full_name = full_name_var.get().strip()
    if not full_name:
        messagebox.showwarning("Missing field", "Please enter a customer full name.")
        return

    success, result, _ = search_customer(full_name)
    output_text.config(state="normal")
    output_text.delete("1.0", tk.END)
    if not success:
        status_label.config(text=result)
        output_text.config(state="disabled")
        return

    customer_info = result
    output_text.insert(tk.END, f"Customer: {customer_info['first_name']} {customer_info['last_name']}\n")
    output_text.insert(tk.END, f"Email: {customer_info['email']}\n")
    output_text.insert(tk.END, f"Phone: {customer_info['phone']}\n")
    output_text.insert(tk.END, f"Registered: {customer_info['created_at']}\n\n")

    orders = customer_info["orders"]
    if not orders:
        output_text.insert(tk.END, "This customer has no orders yet.\n")
    else:
        for order_id, product_name, quantity, price, order_date in orders:
            shipping = get_shipping_for_order(order_id)
            total_amount = quantity * price
            output_text.insert(tk.END, f"Order ID: {order_id}\n")
            output_text.insert(tk.END, f"Product: {product_name}\n")
            output_text.insert(tk.END, f"Quantity: {quantity}\n")
            output_text.insert(tk.END, f"Price per item: {price:.2f}\n")
            output_text.insert(tk.END, f"Total amount: {total_amount:.2f}\n")
            output_text.insert(tk.END, f"Order date: {order_date}\n")
            if shipping:
                address, city, postal_code, country, status_value, shipped_date = shipping
                output_text.insert(tk.END, "Shipping:\n")
                output_text.insert(tk.END, f"  Address: {address}\n")
                output_text.insert(tk.END, f"  City: {city}\n")
                output_text.insert(tk.END, f"  Postal code: {postal_code}\n")
                output_text.insert(tk.END, f"  Country: {country}\n")
                output_text.insert(tk.END, f"  Status: {status_value}\n")
                if shipped_date:
                    output_text.insert(tk.END, f"  Shipped date: {shipped_date}\n")
            else:
                output_text.insert(tk.END, "Shipping: Pending\n")
            output_text.insert(tk.END, "\n")

    status_label.config(text="Search completed.")
    output_text.config(state="disabled")


def refresh_customers_list(customers_text, status_label):
    """Refresh the customers list in the GUI."""
    customers = list_customers_data()
    customers_text.config(state="normal")
    customers_text.delete("1.0", tk.END)
    if not customers:
        customers_text.insert(tk.END, "No registered customers yet.\n")
    else:
        for customer_id, first_name, last_name, email in customers:
            customers_text.insert(tk.END, f"{customer_id}: {first_name} {last_name} ({email})\n")
    customers_text.config(state="disabled")
    status_label.config(text="Customer list refreshed.")


def create_all_orders_tab(notebook):
    """Create the All Orders tab for viewing all orders."""
    frame = ttk.Frame(notebook, padding=12)
    status_label = ttk.Label(frame, text="Click Refresh to view all orders.")
    orders_text = tk.Text(frame, width=72, height=20, wrap="word", state="disabled")

    def refresh_orders_view():
        orders = get_all_orders_data()
        orders_text.config(state="normal")
        orders_text.delete("1.0", tk.END)
        if not orders:
            orders_text.insert(tk.END, "No orders yet.\n")
        else:
            for oid, product, quantity, price, order_date, fname, lname in orders:
                shipping = get_shipping_for_order(oid)
                total_amount = quantity * price
                orders_text.insert(tk.END, f"Order ID: {oid}\n")
                orders_text.insert(tk.END, f"Customer: {fname} {lname}\n")
                orders_text.insert(tk.END, f"Product: {product}\n")
                orders_text.insert(tk.END, f"Quantity: {quantity}\n")
                orders_text.insert(tk.END, f"Price per item: {price:.2f}\n")
                orders_text.insert(tk.END, f"Total amount: {total_amount:.2f}\n")
                orders_text.insert(tk.END, f"Order date: {order_date}\n")
                if shipping:
                    address, city, postal_code, country, status_value, shipped_date = shipping
                    orders_text.insert(tk.END, "Shipping:\n")
                    orders_text.insert(tk.END, f"  Address: {address}\n")
                    orders_text.insert(tk.END, f"  City: {city}\n")
                    orders_text.insert(tk.END, f"  Postal code: {postal_code}\n")
                    orders_text.insert(tk.END, f"  Country: {country}\n")
                    orders_text.insert(tk.END, f"  Status: {status_value}\n")
                    if shipped_date:
                        orders_text.insert(tk.END, f"  Shipped date: {shipped_date}\n")
                else:
                    orders_text.insert(tk.END, "Shipping: Pending\n")
                orders_text.insert(tk.END, "\n")
        orders_text.config(state="disabled")
        status_label.config(text="All orders refreshed.")

    ttk.Button(frame, text="Refresh All Orders", command=refresh_orders_view).grid(row=0, column=0, sticky="w", pady=4)
    status_label.grid(row=1, column=0, sticky="w", pady=4)
    orders_text.grid(row=2, column=0, pady=(10, 0))
    return frame


def create_register_tab(notebook):
    """Create the Register tab for adding new customers."""
    frame = ttk.Frame(notebook, padding=12)
    first_name_var = tk.StringVar()
    last_name_var = tk.StringVar()
    email_var = tk.StringVar()
    phone_var = tk.StringVar()
    status_label = ttk.Label(frame, text="Enter customer details and click Register.")

    fields = [
        ("First name:", first_name_var),
        ("Last name:", last_name_var),
        ("Email:", email_var),
        ("Phone:", phone_var),
    ]

    for row, (label_text, var) in enumerate(fields):
        ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=var, width=40).grid(row=row, column=1, sticky="w", pady=4)

    ttk.Button(
        frame,
        text="Register Customer",
        command=lambda: register_customer_gui(first_name_var, last_name_var, email_var, phone_var, status_label),
    ).grid(row=len(fields), column=0, columnspan=2, pady=10)
    status_label.grid(row=len(fields) + 1, column=0, columnspan=2, sticky="w")
    return frame


def create_order_tab(notebook):
    """Create the Orders tab for adding new orders."""
    frame = ttk.Frame(notebook, padding=12)
    customer_combo_var = tk.StringVar()
    product_name_var = tk.StringVar()
    quantity_var = tk.StringVar()
    price_var = tk.StringVar()
    status_label = ttk.Label(frame, text="Select a customer and fill in order details.")

    ttk.Label(frame, text="Customer:").grid(row=0, column=0, sticky="w", pady=4)
    customer_combo = ttk.Combobox(frame, textvariable=customer_combo_var, values=get_customers_for_combobox(), state="readonly", width=37)
    customer_combo.grid(row=0, column=1, sticky="w", pady=4)

    ttk.Label(frame, text="Product name:").grid(row=1, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=product_name_var, width=40).grid(row=1, column=1, sticky="w", pady=4)

    ttk.Label(frame, text="Quantity:").grid(row=2, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=quantity_var, width=40).grid(row=2, column=1, sticky="w", pady=4)

    ttk.Label(frame, text="Price per item:").grid(row=3, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=price_var, width=40).grid(row=3, column=1, sticky="w", pady=4)

    def refresh_customers():
        customer_combo['values'] = get_customers_for_combobox()
        status_label.config(text="Customer list refreshed.")

    ttk.Button(frame, text="Refresh Customers", command=refresh_customers).grid(row=4, column=0, pady=4)
    ttk.Button(
        frame,
        text="Add Order",
        command=lambda: insert_order_gui(customer_combo_var, product_name_var, quantity_var, price_var, status_label),
    ).grid(row=4, column=1, pady=10)
    status_label.grid(row=5, column=0, columnspan=2, sticky="w")
    return frame


def create_shipping_tab(notebook):
    """Create the Shipping tab for adding shipping details."""
    frame = ttk.Frame(notebook, padding=12)
    order_combo_var = tk.StringVar()
    address_var = tk.StringVar()
    city_var = tk.StringVar()
    postal_code_var = tk.StringVar()
    country_var = tk.StringVar()
    status_var = tk.StringVar()
    status_label = ttk.Label(frame, text="Select an order and fill in shipping details.")

    ttk.Label(frame, text="Order:").grid(row=0, column=0, sticky="w", pady=4)
    order_combo = ttk.Combobox(frame, textvariable=order_combo_var, values=get_orders_for_combobox(), state="readonly", width=37)
    order_combo.grid(row=0, column=1, sticky="w", pady=4)

    ttk.Label(frame, text="Address:").grid(row=1, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=address_var, width=40).grid(row=1, column=1, sticky="w", pady=4)

    ttk.Label(frame, text="City:").grid(row=2, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=city_var, width=40).grid(row=2, column=1, sticky="w", pady=4)

    ttk.Label(frame, text="Postal code:").grid(row=3, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=postal_code_var, width=40).grid(row=3, column=1, sticky="w", pady=4)

    ttk.Label(frame, text="Country:").grid(row=4, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=country_var, width=40).grid(row=4, column=1, sticky="w", pady=4)

    ttk.Label(frame, text="Status:").grid(row=5, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=status_var, width=40).grid(row=5, column=1, sticky="w", pady=4)

    def refresh_orders():
        order_combo['values'] = get_orders_for_combobox()
        status_label.config(text="Order list refreshed.")

    ttk.Button(frame, text="Refresh Orders", command=refresh_orders).grid(row=6, column=0, pady=4)
    ttk.Button(
        frame,
        text="Add Shipping",
        command=lambda: add_shipping_gui(order_combo_var, address_var, city_var, postal_code_var, country_var, status_var, status_label),
    ).grid(row=6, column=1, pady=10)
    status_label.grid(row=7, column=0, columnspan=2, sticky="w")
    return frame


def create_search_tab(notebook):
    """Create the Search tab for finding customers."""
    frame = ttk.Frame(notebook, padding=12)
    full_name_var = tk.StringVar()
    status_label = ttk.Label(frame, text="Search a customer by full name.")
    output_text = tk.Text(frame, width=72, height=16, wrap="word", state="disabled")

    ttk.Label(frame, text="Customer full name:").grid(row=0, column=0, sticky="w", pady=4)
    ttk.Entry(frame, textvariable=full_name_var, width=40).grid(row=0, column=1, sticky="w", pady=4)
    ttk.Button(
        frame,
        text="Search",
        command=lambda: search_customer_gui(full_name_var, output_text, status_label),
    ).grid(row=1, column=0, columnspan=2, pady=10)
    status_label.grid(row=2, column=0, columnspan=2, sticky="w")
    output_text.grid(row=3, column=0, columnspan=2, pady=(10, 0))
    return frame


def create_customer_list_tab(notebook):
    """Create the Customers tab for viewing all customers."""
    frame = ttk.Frame(notebook, padding=12)
    status_label = ttk.Label(frame, text="Refresh the list to see all registered customers.")
    customers_text = tk.Text(frame, width=72, height=16, wrap="word", state="disabled")

    ttk.Button(
        frame,
        text="Refresh Customers",
        command=lambda: refresh_customers_list(customers_text, status_label),
    ).grid(row=0, column=0, sticky="w", pady=4)
    status_label.grid(row=1, column=0, sticky="w", pady=4)
    customers_text.grid(row=2, column=0, pady=(10, 0))
    return frame


def main():
    """Main function to initialize the database and launch the GUI."""
    initialize_db()
    root = tk.Tk()
    root.title("Customer Orders & Shipping Manager")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    notebook.add(create_register_tab(notebook), text="Register")
    notebook.add(create_order_tab(notebook), text="Orders")
    notebook.add(create_shipping_tab(notebook), text="Shipping")
    notebook.add(create_search_tab(notebook), text="Search")
    notebook.add(create_customer_list_tab(notebook), text="Customers")
    notebook.add(create_all_orders_tab(notebook), text="All Orders")

    root.mainloop()


if __name__ == "__main__":
    main()
