# Inventory Management Web Application

This is a Flask-based Inventory Management Web Application that uses PostgreSQL for backend data storage. It allows users to manage products, warehouse locations, product movements, and view inventory details in a user-friendly interface.

---

## Features

- **Register Products and Locations**: Add new products and warehouse locations with validation for consistency in IDs and names.
- **Record Product Quantities**: Insert products into specific locations with quantity.
- **Edit Products**: Update product names, locations, and quantities.
- **Delete Entries**: Remove a specific product-location pair from inventory.
- **View Inventory**: Display all current product-location-quantity entries.
- **Product Movement**: Move products between locations while maintaining quantity balances.
- **Inventory by Location**: View all products and their quantities in a specific location.
- **Validation**: Checks for mismatches in product and location IDs/names to prevent data conflicts.

---

## Technologies Used

- **Backend**: Python 3, Flask
- **Database**: PostgreSQL
- **Frontend**: HTML, Bootstrap (assumed based on `render_template` usage)

---

## Database Schema

You will need the following tables:

## sql

CREATE TABLE Product (
    product_id INT PRIMARY KEY,
    product_name TEXT UNIQUE
);

CREATE TABLE Location (
    location_id INT PRIMARY KEY,
    location TEXT UNIQUE
);

CREATE TABLE Products (
    product_id INT,
    location TEXT,
    quantity INT,
    PRIMARY KEY (product_id, location)
);

CREATE TABLE Inventory (
    product_id INT,
    location_id INT,
    quantity INT,
    PRIMARY KEY (product_id, location_id)
);

CREATE TABLE ProductMovement (
    id SERIAL PRIMARY KEY,
    product_id INT,
    qty INT,
    from_location INT,
    to_location INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Setup Instructions

1.Clone the Repository

git clone https://github.com/your-username/inventory-management-flask.git
cd inventory-management-flask

2.Create a Virtual Environment

python -m venv venv
source venv/bin/activate 

3.Install Dependencies

pip install Flask psycopg2

4.Configure PostgreSQL

*Ensure PostgreSQL is installed and running.
*Create a database named flask.
*Update credentials in the get_connection() function in the app.py file if needed.

5.Create the Tables

Execute the SQL schema above in your PostgreSQL database.

6.Run the Application

python app.py
Navigate to http://localhost:5000 in your browser.

Folder Structure
    
      
      ├── templates/
      │   ├── register.html
      │   ├── confirm.html
      │   ├── view.html
      │   ├── edit.html
      │   ├── add_movement.html
      │   ├── view_movements.html
      │   └── check_inventory.html
      │   └── location_inventory.html
      ├── app.py
      └── README.md
![Screenshot 2025-05-05 202602](https://github.com/user-attachments/assets/2b20852f-367e-4e52-9262-f8dd6348ec70)


