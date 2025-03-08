from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '2021260401gg',
    'database': 'car_rental'
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cars")
    cars = cursor.fetchall()
    for car in cars:
        cursor.execute("SELECT * FROM rental_prices WHERE car_id = %s", (car['id'],))
        car['prices'] = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', cars=cars)


@app.route('/car/<int:car_id>')
def car_detail(car_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cars WHERE id = %s", (car_id,))
    car = cursor.fetchone()
    cursor.execute("SELECT * FROM rental_prices WHERE car_id = %s", (car_id,))
    prices = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('car_detail.html', car=car, prices=prices)


@app.route('/upload', methods=['GET', 'POST'])
def upload_car():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        license_plate = request.form['license_plate']
        photo = request.files['photo']
        photo_filename = photo.filename
        photo.save(f'static/uploads/{photo_filename}')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cars (название, категория, гос_номер, фото) VALUES (%s, %s, %s, %s)",
                       (name, category, license_plate, photo_filename))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('upload.html')


@app.route('/rent', methods=['POST'])
def rent_car():
    car_id = request.form['car_id']
    rent_period = request.form['rent_period']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT цена FROM rental_prices WHERE car_id = %s AND срок = %s", (car_id, rent_period))
    price = cursor.fetchone()
    cursor.close()
    conn.close()
    if price:
        total_cost = price['цена']
    else:
        total_cost = "Цена не найдена"

    return render_template('rent_result.html', total_cost=total_cost)


@app.route('/category/<string:category>')
def show_category(category):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cars WHERE категория = %s", (category,))
    cars = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('category.html', cars=cars, category=category)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


if __name__ == '__main__':
    app.run(debug=True)