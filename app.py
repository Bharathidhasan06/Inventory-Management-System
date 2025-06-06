import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        dbname="flask",
        user="postgres",
        password="JayashriBharathi",
        host="localhost"
    )

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        return redirect(url_for('register'))
    return render_template('login.html')


@app.route("/confirm", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        i = request.form.get("product_id")
        n = request.form.get("product")
        l = request.form.get("location_id")
        a = request.form.get("location")
        qty = request.form.get("quantity")
        price=request.form.get("price")

        if not i.isdigit() or int(i) <= 0 or not l.isdigit() or int(l) <= 0:
            return render_template("register.html", error_message="Invalid Product ID or Location ID. IDs must be positive integers.")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT product_name FROM Product WHERE product_id = %s", (i,))
        row = cur.fetchone()
        if row and row[0] != n:
            cur.close()
            conn.close()
            return render_template("register.html", error_message="Product ID already exists with a different name. Please use a different ID or correct the name.",
                                   product_id=i, product=n, location_id=l, location=a)

        cur.execute("SELECT product_id FROM Product WHERE product_name = %s", (n,))
        existing = cur.fetchone()
        if existing and str(existing[0]) != i:
            cur.close()
            conn.close()
            return render_template("register.html", error_message="Product name already exists with a different ID. Please use a different name or correct the ID.",
                                   product_id=i, product=n, location_id=l, location=a)

        cur.execute("SELECT location FROM Location WHERE location_id = %s", (l,))
        row = cur.fetchone()
        if row and row[0] != a:
            cur.close()
            conn.close()
            return render_template("register.html", error_message="Location ID already exists with a different name. Please use a different ID or correct the name.",
                                   product_id=i, product=n, location_id=l, location=a)

        cur.execute("SELECT location_id FROM Location WHERE location = %s", (a,))
        existing = cur.fetchone()
        if existing and str(existing[0]) != l:
            cur.close()
            conn.close()
            return render_template("register.html", error_message="Location name already exists with a different ID. Please use a different name or correct the ID.",
                                   product_id=i, product=n, location_id=l, location=a)

        cur.execute("INSERT INTO Product (product_id, product_name,price) VALUES (%s, %s,%s) ON CONFLICT DO NOTHING", (i, n,price))
        cur.execute("INSERT INTO Location (location_id, location) VALUES (%s, %s) ON CONFLICT DO NOTHING", (l, a))

        cur.execute("""INSERT INTO Products (product_id, location, quantity,price) VALUES (%s, %s, %s,%s) ON CONFLICT (product_id, location) DO UPDATE SET quantity = Products.quantity + EXCLUDED.quantity""", (i, a, qty,price))

        cur.execute("""INSERT INTO Inventory (product_id, location_id, quantity) VALUES (%s, %s, %s) ON CONFLICT (product_id, location_id) DO UPDATE SET quantity = Inventory.quantity + EXCLUDED.quantity""", (i, l, qty))

        conn.commit()

        cur.execute("SELECT product_name FROM Product WHERE product_id = %s", (i,))
        product_name = cur.fetchone()[0]
        cur.execute("SELECT location FROM Location WHERE location_id = %s", (l,))
        location = cur.fetchone()[0]
        cur.execute("SELECT price FROM products WHERE product_id=%s AND location =%s", (i,a))
        price=cur.fetchone()[0]
        cur.close()
        conn.close()

        return render_template("confirm.html", product_id=i, product_name=product_name, location_id=l, location=location, quantity=qty,price=price)

    return render_template('register.html')



@app.route("/view")
def view_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(""" 
    SELECT p.product_id, pr.product_name, p.location, p.quantity, p.price FROM Products p JOIN Product pr ON p.product_id = pr.product_id""")

    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("view.html", products=products)


@app.route("/delete/<string:product_id>/<string:location>", methods=["GET"])
def delete_product(product_id, location):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(""" DELETE FROM Products  WHERE product_id = %s AND location = %s """, (product_id, location))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('view_products'))


@app.route("/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" SELECT p.product_id, p.product_name, pl.location_id, pl.location, pr.quantity,pr.price FROM Products pr JOIN Product p ON pr.product_id = p.product_id JOIN Location pl ON pr.location = pl.location WHERE p.product_id = %s """, (product_id,))
    product = cur.fetchone()

    if product:
        product_id, product_name, location_id, location_name,quantity,price=product
    else:
        return "Product not found."
    if request.method == "POST":
        new_product_name = request.form["product"]
        new_location_name = request.form["location"]
        new_quantity = request.form["quantity"]
        new_price=request.form["price"]
        cur.execute(""" UPDATE Product SET product_name = %s , price=%s WHERE product_id = %s """, (new_product_name,new_price, product_id))

        cur.execute(""" UPDATE Location SET location = %s WHERE location_id = %s """, (new_location_name, location_id))

        cur.execute(""" UPDATE Products SET quantity = %s  , price=%s WHERE product_id = %s AND location = %s """, (new_quantity,new_price, product_id, location_name))

        ##cur.execute(""" UPDATE Products SET  WHERE product_id=%s """,(new_price,product_id))

       

        

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('view_products'))

    cur.close()
    conn.close()

    return render_template("edit.html", product_id=product_id, product_name=product_name, location_id=location_id, location_name=location_name, quantity=quantity)



@app.route('/movement', methods=['GET', 'POST'])
def add_movement():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT product_id, product_name FROM Product")
    products = cur.fetchall()
    cur.execute("SELECT location_id, location FROM Location")
    locations = cur.fetchall()
    
    if request.method == 'POST':
        product_id = request.form['product_id']
        from_location = request.form['from_location'] or None
        to_location = request.form['to_location'] or None
        qty = int(request.form['qty'])


        if qty <= 0:
            error_message = "Please provide a valid quantity."
            cur.close()
            conn.close()
            return render_template('add_movement.html', products=products, locations=locations, error_message=error_message)
        
        if qty>10 :
            error_message="Quantity should be Lesser than or equal to 10"
            cur.close()
            conn.close()
            return render_template('add_movement.html',products=products,locations=locations,error_message=error_message)

        if not from_location and not to_location:
            error_message = 'Please select either a "From" or "To" location.'
            cur.close()
            conn.close()
            return render_template('add_movement.html', products=products, locations=locations, error_message=error_message)

        from_location_name = None
        to_location_name = None

        if from_location:
            cur.execute("SELECT location FROM Location WHERE location_id = %s", (from_location,))
            from_location_name = cur.fetchone()[0]

            cur.execute(""" SELECT quantity FROM Products  WHERE product_id = %s AND location = %s """, (product_id, from_location_name))
            result = cur.fetchone()

            if not result or result[0] < qty:
                cur.close()
                conn.close()
                error_message = "Product not present in warehouse or insufficient quantity."
                return render_template('add_movement.html', products=products, locations=locations, error_message=error_message)

            cur.execute(""" UPDATE Products SET quantity = quantity - %s  WHERE product_id = %s AND location = %s """, (qty, product_id, from_location_name))

            cur.execute(""" DELETE FROM Products  WHERE product_id = %s AND location = %s AND quantity = 0 """, (product_id, from_location_name))
        if to_location:
            cur.execute("SELECT location FROM Location WHERE location_id = %s", (to_location,))
            to_location_name = cur.fetchone()[0]

            cur.execute(""" SELECT 1 FROM Products  WHERE product_id = %s AND location = %s """, (product_id, to_location_name))
            if cur.fetchone():
                cur.execute(""" UPDATE Products SET quantity = quantity + %s  WHERE product_id = %s AND location = %s """, (qty, product_id, to_location_name))
            else:
                cur.execute(""" INSERT INTO Products (product_id, location, quantity)  VALUES (%s, %s, %s) """, (product_id, to_location_name, qty))

        cur.execute(""" INSERT INTO ProductMovement (product_id, qty, from_location, to_location)  VALUES (%s, %s, %s, %s) """, (product_id, qty, int(from_location) if from_location else None, int(to_location) if to_location else None))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('view_movements'))

    cur.close()
    conn.close()
    return render_template('add_movement.html', products=products, locations=locations)




@app.route('/view_movements')
def view_movements():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ProductMovement ORDER BY timestamp DESC")
    movements = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('view_movements.html', movements=movements)

@app.route('/check_inventory', methods=['GET', 'POST'])
def check_inventory():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT location_id, location FROM Location")
    locations = cur.fetchall()

    if request.method == 'POST':
        location_id = request.form['location_id']

        cur.execute("SELECT location FROM Location WHERE location_id = %s", (location_id,))
        row = cur.fetchone()

        if not row:
            cur.close()
            conn.close()
            return render_template('check_inventory.html', locations=locations, error_message="Invalid Location ID.")

        location_name = row[0]

        cur.execute(""" SELECT p.product_id, pr.product_name, p.quantity FROM Products p JOIN Product pr ON p.product_id = pr.product_id WHERE p.location = %s """, (location_name,))
        inventory = cur.fetchall()

        cur.close()
        conn.close()

        if not inventory:
            return render_template('location_inventory.html', location_id=location_id, location=location_name, empty=True)

        return render_template('location_inventory.html', location_id=location_id, location=location_name, inventory=inventory)

    cur.close()
    conn.close()
    return render_template('check_inventory.html', locations=locations)


if __name__ == '__main__':
    app.run(debug=True)