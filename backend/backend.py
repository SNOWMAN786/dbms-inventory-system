from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  # Enables frontend requests

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',        # Add your MySQL password if you have one
    'database': 'inventory_db'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ==========================================
# 1. CATEGORIES & SUPPLIERS (For Dropdowns)
# ==========================================

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Categories")
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(categories), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Suppliers")
        suppliers = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(suppliers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 2. PRODUCTS CRUD
# ==========================================

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                p.product_id, 
                p.product_name, 
                c.category_name, 
                s.supplier_name, 
                p.unit_price, 
                p.quantity_in_stock, 
                p.min_stock_level,
                (p.unit_price * p.quantity_in_stock) AS total_value
            FROM Products p
            JOIN Categories c ON p.category_id = c.category_id
            JOIN Suppliers s ON p.supplier_id = s.supplier_id
            ORDER BY p.product_id DESC;
        """
        cursor.execute(query)
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO Products (product_name, category_id, supplier_id, unit_price, quantity_in_stock, min_stock_level)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data['product_name'],
            data['category_id'],
            data['supplier_id'],
            data['unit_price'],
            data['quantity_in_stock'],
            data.get('min_stock_level', 10)
        )
        cursor.execute(query, values)
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Product created successfully", "product_id": new_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            UPDATE Products 
            SET product_name = %s, unit_price = %s, quantity_in_stock = %s, min_stock_level = %s
            WHERE product_id = %s
        """
        values = (data['product_name'], data['unit_price'], data['quantity_in_stock'], data['min_stock_level'], product_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Product updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Products WHERE product_id = %s", (product_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 3. TRANSACTIONS (Sales & Stock Reduction)
# ==========================================

@app.route('/api/sales', methods=['POST'])
def record_sale():
    try:
        data = request.json  # Expects: { "product_id": 1, "quantity": 5, "unit_price": 100.00 }
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert Sale Header
        cursor.execute("INSERT INTO Sales (total_amount) VALUES (%s)", (data['quantity'] * data['unit_price'],))
        sale_id = cursor.lastrowid

        # Insert Sale Item
        cursor.execute(
            "INSERT INTO SaleItems (sale_id, product_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
            (sale_id, data['product_id'], data['quantity'], data['unit_price'])
        )

        # Reduce Stock Quantity
        cursor.execute(
            "UPDATE Products SET quantity_in_stock = quantity_in_stock - %s WHERE product_id = %s",
            (data['quantity'], data['product_id'])
        )

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Sale recorded and stock updated successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 4. REPORTS & VIEWS
# ==========================================

@app.route('/api/reports/low-stock', methods=['GET'])
def get_low_stock():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM View_LowStockProducts")
        low_stock_items = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(low_stock_items), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)