from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import errorcode
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'  # Needed for session management

# Database connection configuration
db_config = {
    'user': 'root',  # Your MySQL username
    'password': '1234',  # Your MySQL password
    'host': '127.0.0.1',  # Your MySQL server host
    'database': 'crime_file_management'  # Your MySQL database name
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/visitor', methods=['GET', 'POST'])
def visitor():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['user_id'] = user['id']
                session['email'] = user['email']
                return redirect(url_for('visitor_home'))
            else:
                flash("Invalid email or password", 'error')
        else:
            flash("Database connection failed", 'error')
    return render_template('visitor.html')

@app.route('/visitor_home')
def visitor_home():
    if 'user_id' in session:
        return render_template('visitor_home.html', email=session['email'])
    return redirect(url_for('visitor'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        admin_id = request.form['admin_id']
        password = request.form['password']
        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM admins WHERE admin_id = %s AND password = %s', (admin_id, password))
            admin = cursor.fetchone()
            conn.close()
            if admin:
                session['admin_id'] = admin_id
                return redirect(url_for('admin_home'))
            else:
                flash("Invalid credentials", 'error')
        else:
            flash("Database connection failed", 'error')
    return render_template('admin.html')


@app.route('/admin_home')
def admin_home():
    if 'admin_id' in session:
        return render_template('admin_home.html')
    return redirect(url_for('admin'))


@app.route('/admin_complaints')
def admin_complaints():
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM complaints")
        complaints = cursor.fetchall()
        conn.close()
        return render_template('admin_complaints.html', complaints=complaints)
    else:
        flash("Database connection failed")
        return redirect(url_for('admin_home'))

@app.route('/admin_witnesses')
def admin_witnesses():
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM crime_reports")
        reports = cursor.fetchall()
        conn.close()
        return render_template('admin_witnesses.html', reports=reports)
    else:
        flash("Database connection failed")
        return redirect(url_for('admin_home'))

@app.route('/admin_missing_persons')
def admin_missing_persons():
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM missing_persons")
        persons = cursor.fetchall()
        conn.close()
        return render_template('admin_missing_persons.html', persons=persons)
    else:
        flash("Database connection failed")
        return redirect(url_for('admin_home'))

@app.route('/admin_add_fir', methods=['GET', 'POST'])
def admin_add_fir():
    if request.method == 'POST':
        name = request.form['name']
        missing_place = request.form['missing_place']
        date_of_missing = request.form['date_of_missing']
        age = request.form['age']
        weight = request.form['weight']
        height = request.form['height']
        address_of_missing = request.form['address_of_missing']
        date_of_report = request.form['date_of_report']
        fir_number = request.form['fir_number']
        act_no = request.form['act_no']

        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO fir_reports (name, missing_place, date_of_missing, age, weight, height, address_of_missing, date_of_report, fir_number, act_no) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                           (name, missing_place, date_of_missing, age, weight, height, address_of_missing, date_of_report, fir_number, act_no))
            conn.commit()
            conn.close()
            flash("You have successfully submitted the FIR report", 'success')
        else:
            flash("Database connection failed", 'error')
    return render_template('admin_add_fir.html')

@app.route('/admin_add_wanted', methods=['GET', 'POST'])
def admin_add_wanted():
    if request.method == 'POST':
        name = request.form['name']
        sex = request.form['sex']
        age = request.form['age']
        height = request.form['height']
        act = request.form['act']
        brief_of_case = request.form['brief_of_case']
        picture = request.files['picture']

        picture_filename = None
        if picture:
            picture_filename = picture.filename
            picture.save(os.path.join('static/uploads', picture_filename))

        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO wanted_list (name, sex, age, height, act, brief_of_case, picture) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                               (name, sex, age, height, act, brief_of_case, picture_filename))
                cursor.execute('INSERT INTO visitors_wanted_list (name, sex, age, height, act, brief_of_case, picture) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                               (name, sex, age, height, act, brief_of_case, picture_filename))
                conn.commit()
                flash("You have successfully submitted.", 'success')
            except:
                flash("Something went wrong. Please try again.", 'error')
            finally:
                conn.close()
            return redirect(url_for('admin_add_wanted'))
        else:
            flash("Database connection failed", 'error')
    return render_template('admin_add_wanted.html')

@app.route('/admin_wanted_list')
def admin_wanted_list():
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM wanted_list")
        criminals = cursor.fetchall()
        conn.close()
        return render_template('admin_wanted_list.html', criminals=criminals)
    else:
        flash("Database connection failed")
        return redirect(url_for('admin_home'))

@app.route('/admin_logout')
def admin_logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        state = request.form['state']
        country = request.form['country']

        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (name, email, password, date_of_birth, gender, phone_number, state, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
                               (name, email, password, date_of_birth, gender, phone_number, state, country))
                conn.commit()
                flash("You have successfully registered! Log in now.", "success")
            except mysql.connector.IntegrityError:
                conn.close()
                flash("Email already exists", "error")
                return redirect(url_for('register'))
            conn.close()
            return redirect(url_for('register'))
        else:
            flash("Database connection failed", "error")
            return redirect(url_for('register'))
    return render_template('register.html')
@app.route('/complaints', methods=['GET', 'POST'])
def complaints():
    if request.method == 'POST':
        user_name = request.form['user_name']
        suspect_details = request.form['suspect_details']
        description = request.form['description']
        date_of_complaint = request.form['date_of_complaint']
        type_of_complaint = request.form['type_of_complaint']

        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO complaints (user_name, suspect_details, description, date_of_complaint, type_of_complaint) VALUES (%s, %s, %s, %s, %s)', 
                               (user_name, suspect_details, description, date_of_complaint, type_of_complaint))
                conn.commit()
                flash("Complaint added successfully", 'success')
            except:
                flash("Something went wrong. Please try again.", 'error')
            finally:
                conn.close()
            return redirect(url_for('complaints'))
        else:
            flash("Database connection failed", 'error')
    return render_template('complaints.html')

@app.route('/crime_report', methods=['GET', 'POST'])
def crime_report():
    if request.method == 'POST':
        suspect_name = request.form['suspect_name']
        informer_name = request.form['informer_name']
        informer_address = request.form['informer_address']
        description = request.form['description']
        date_of_report = request.form['date_of_report']

        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO crime_reports (suspect_name, informer_name, informer_address, description, date_of_report) VALUES (%s, %s, %s, %s, %s)', 
                               (suspect_name, informer_name, informer_address, description, date_of_report))
                conn.commit()
                flash("Crime report added successfully", 'success')
            except:
                flash("Something went wrong. Please try again.", 'error')
            finally:
                conn.close()
            return redirect(url_for('crime_report'))
        else:
            flash("Database connection failed", 'error')
    return render_template('crime_report.html')

@app.route('/missing_person', methods=['GET', 'POST'])
def missing_person():
    if request.method == 'POST':
        name = request.form['name']
        missing_place = request.form['missing_place']
        date_of_missing = request.form['date_of_missing']
        sex = request.form['sex']
        age = request.form['age']
        height = request.form['height']
        weight = request.form['weight']
        brief_of_case = request.form['brief_of_case']
        address_of_missing = request.form['address_of_missing']
        date_of_report = request.form['date_of_report']
        picture = request.files['picture']

        picture_filename = None
        if picture:
            picture_filename = picture.filename
            picture.save(os.path.join('static/uploads', picture_filename))

        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO missing_persons (name, missing_place, date_of_missing, sex, age, height, weight, brief_of_case, address_of_missing, date_of_report, picture) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                               (name, missing_place, date_of_missing, sex, age, height, weight, brief_of_case, address_of_missing, date_of_report, picture_filename))
                conn.commit()
                flash("Missing person report added successfully", 'success')
            except:
                flash("Something went wrong. Please try again.", 'error')
            finally:
                conn.close()
            return redirect(url_for('missing_person'))
        else:
            flash("Database connection failed", 'error')
    return render_template('missing_person.html')


@app.route('/edit_complaint', methods=['GET', 'POST'])
def edit_complaint():
    if request.method == 'POST':
        user_name = request.form['user_name']
        suspect_details = request.form['suspect_details']
        description = request.form['description']
        date_of_complaint = request.form['date_of_complaint']
        type_of_complaint = request.form['type_of_complaint']

        conn = get_db_connection()
        if conn is not None:
            cursor = conn.cursor()
            try:
                cursor.execute('UPDATE complaints SET suspect_details=%s, description=%s, date_of_complaint=%s, type_of_complaint=%s WHERE user_name=%s', 
                               (suspect_details, description, date_of_complaint, type_of_complaint, user_name))
                conn.commit()
                flash("You have successfully submitted your complaint", 'success')
            except:
                flash("Something went wrong. Please try again.", 'error')
            finally:
                conn.close()
            return redirect(url_for('edit_complaint'))
        else:
            flash("Database connection failed", 'error')
    return render_template('edit_complaint.html')


@app.route('/wanted_list')
def wanted_list():
    conn = get_db_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM visitors_wanted_list")
        criminals = cursor.fetchall()
        conn.close()
        return render_template('wanted_list.html', criminals=criminals)
    else:
        flash("Database connection failed")
        return redirect(url_for('visitor_home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
