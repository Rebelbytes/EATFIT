from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Kisanjena@123'
app.config['MYSQL_DB'] = 'user_database'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user:
            # Add password reset email logic here if desired
            flash('Password reset instructions have been sent to your email.', 'info')
        else:
            flash('Email address not found.', 'danger')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/get_started')
def get_started():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Landing Page
@app.route('/')
def landing_page():
    return render_template('landing_page.html')

# Sign Up Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email already exists. Please use a different email address.', 'danger')
            return redirect(url_for('signup'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                    (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('You have successfully signed up!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

# Login Page – after login, redirect to health form
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cur.fetchone()
        cur.close()
        if not user or not bcrypt.check_password_hash(user[3], password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
        session['user_id'] = user[0]
        session['user_email'] = user[2]
        flash('Login successful!', 'success')
        # Redirect to health form after login
        return redirect(url_for('health_form'))
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing_page'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    return render_template('page1.html')

# Health Form Page
@app.route('/health_form')
def health_form():
    if 'user_id' not in session:
        flash('Please log in to access the health form.', 'warning')
        return redirect(url_for('login'))
    return render_template('healthForm.html')

# Process Health Form Submission: Calculate BMI, store data, and redirect to landing page
@app.route('/submit_health_data', methods=['POST'])
def submit_health_data():
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    try:
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        age = int(request.form['age'])
    except ValueError:
        flash('Invalid input for height, weight, or age.', 'danger')
        return redirect(url_for('health_form'))
    diabetes = request.form['diabetes']
    bp = request.form['bp']
    cholesterol = request.form['cholesterol']
    
    # Convert height from feet to meters and calculate BMI
    height_m = height * 0.3048
    bmi = round(weight / (height_m ** 2), 2)
    
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO health_data (user_id, height, weight, bmi, age, diabetes, bp, cholesterol)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (user_id, height, weight, bmi, age, diabetes, bp, cholesterol))
    mysql.connection.commit()
    cur.close()
    
    flash('Health data submitted successfully!', 'success')
    # Redirect to landing page after submission
    return redirect(url_for('landing_page'))

# Profile Page: Display user details and the most recent health data (including BMI)
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Access denied, please log in.', 'warning')
        return redirect(url_for('landing_page'))
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", (name, email, user_id))
        if 'profile_image' in request.files:
            image = request.files['profile_image']
            if image and allowed_file(image.filename):
                image_data = image.read()
                cur.execute("UPDATE users SET profile_image = %s WHERE id = %s", (image_data, user_id))
        mysql.connection.commit()
        cur.close()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT username, email, profile_image FROM users WHERE id = %s", [user_id])
    user_data = cur.fetchone()
    # Retrieve the most recent health data for the user
    cur.execute("SELECT * FROM health_data WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    health_info = cur.fetchone()
    cur.close()
    
    username, email, profile_image = user_data
    image_url = url_for('get_profile_image') if profile_image else url_for('static', filename='default-avatar.png')
    
    return render_template('profile.html', username=username, email=email, image_url=image_url, health_info=health_info)

@app.route('/get_profile_image')
def get_profile_image():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT profile_image FROM users WHERE id = %s", [user_id])
    profile_image = cur.fetchone()[0]
    cur.close()
    if profile_image:
        return send_file(io.BytesIO(profile_image), mimetype='image/png')
    else:
        return redirect(url_for('static', filename='default-avatar.png'))

# Additional Pages
@app.route('/page2')
def page2():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('page2.html')

@app.route('/summary')
def summary():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('summary.html')

@app.route('/sentiment')
def sentiment():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('sentiment.html')

@app.route('/titlepage')
def titlepage():
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('titlepage.html')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
