from flask_wtf.csrf import CSRFProtect
from flask_uploads import UploadSet, IMAGES, configure_uploads
import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from datetime import datetime, timedelta

photos = UploadSet('photos', IMAGES)
app = Flask(__name__)
csrf = CSRFProtect(app) 
app.config['UPLOADED_PHOTOS_DEST'] = 'static/uploads'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secretkey123') 
configure_uploads(app, photos)

DATABASE_PATH = os.path.abspath('/home/yuds/Flask/siswa.db')
print(f"Database Path: {DATABASE_PATH}")


def get_db():
    print("Attempting to connect to the database...")
    try:
        db = sqlite3.connect(DATABASE_PATH)
        db.row_factory = sqlite3.Row 
        print("Database connection successful.")
        return db
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise


def init_db():
    try:
        with get_db() as db:
            print("Initializing database...")
            db.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    photo_path TEXT
                )
            """)
            print("Students table created (if not exists) with photo_path")
            db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    reset_token TEXT,
                    reset_token_expiry DATETIME
                )
            """)
            print("Users table created (if not exists)")
            db.commit()
            print("Database initialization complete.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")


init_db()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__ 
    return decorated_function


@app.route('/')
@login_required
def index():
    db = get_db()
    students = db.execute("SELECT * FROM students").fetchall()
    db.close()
    return render_template('index.html', siswa=students)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_siswa():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '0')
        photo = request.files.get('photo')
        photo_path = None

        # Name Validation
        if len(name) < 3:
            flash('Name must be at least 3 characters!', 'error')
            return redirect(url_for('add_siswa'))

        try:
            age = int(age)
            if age < 10 or age > 50: 
                flash('Age must be between 10 and 50!', 'error')
                return redirect(url_for('add_siswa'))
        except ValueError:
            flash('Age must be a positive number!', 'error')
            return redirect(url_for('add_siswa'))

        if not photo or photo.filename == '':
            flash('Photo must be uploaded!', 'error')
            return redirect(url_for('add_siswa'))

        if not allowed_file(photo.filename):
            flash('File format not supported! (Only JPG/PNG)', 'error')
            return redirect(url_for('add_siswa'))
        if photo.content_length > 2 * 1024 * 1024:
            flash('Maximum file size is 2MB!', 'error')
            return redirect(url_for('add_siswa'))

        # Upload Photo
        try:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
            photo_path = filename
        except Exception as e:
            flash('Failed to upload photo.', 'error')
            return redirect(url_for('add_siswa'))

        db = get_db()
        try:
            db.execute(
                "INSERT INTO students (name, age, photo_path) VALUES (?, ?, ?)",
                (name, age, photo_path)
            )
            db.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('index'))
        except sqlite3.Error as e: 
            db.rollback()
            flash(f'An error occurred while saving data: {e}', 'error')
            return redirect(url_for('add_siswa'))
        finally:
            db.close()

    return render_template('add.html')


@app.route('/update/<int:index>', methods=['GET', 'POST'])
@login_required
def update_siswa(index):
    db = get_db()
    siswa = db.execute("SELECT * FROM students WHERE id = ?", (index,)).fetchone()
    if not siswa:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age', '0')
        photo = request.files.get('photo')
        delete_photo = request.form.get('delete_photo')
        photo_path = siswa['photo_path']

        if len(name) < 3:
            flash('Name must be at least 3 characters!', 'error')
            return redirect(url_for('update_siswa', index=index))

        try:
            age = int(age)
            if age < 10 or age > 50: 
                flash('Age must be between 10 and 50!', 'error')
                return redirect(url_for('update_siswa', index=index))
        except ValueError:
            flash('Age must be a positive number!', 'error')
            return redirect(url_for('update_siswa', index=index))

        if delete_photo:
            if siswa['photo_path']:
                try:
                    os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], siswa['photo_path']))
                except Exception as e:
                    flash('Failed to delete old photo.', 'error')
            photo_path = None

        if photo and photo.filename != '':
            if not allowed_file(photo.filename):
                flash('File format not supported! (Only JPG/PNG)', 'error')
                return redirect(url_for('update_siswa', index=index))
            if photo.content_length > 2 * 1024 * 1024:
                flash('Maximum file size is 2MB!', 'error')
                return redirect(url_for('update_siswa', index=index))

            try:
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename))
                photo_path = filename
            except Exception as e:
                flash('Failed to upload new photo.', 'error')
                return redirect(url_for('update_siswa', index=index))

        try:
            db.execute(
                "UPDATE students SET name = ?, age = ?, photo_path = ? WHERE id = ?",
                (name, age, photo_path, index)
            )
            db.commit()
        except sqlite3.Error as e:
            db.rollback()
            flash(f'An error occurred while updating data: {e}', 'error')
        finally:
            db.close()

        flash('Student data updated successfully!', 'success')
        return redirect(url_for('index'))

    db.close()
    return render_template('update.html', siswa=siswa)


@app.route('/delete/<int:index>', methods=['POST'])
@login_required
def delete_siswa(index):
    db = get_db()
    siswa = db.execute("SELECT * FROM students WHERE id = ?", (index,)).fetchone()

    if not siswa:
        abort(404)

    try:
        if siswa['photo_path']:
            os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], siswa['photo_path']))
    except Exception as e:
        flash('Failed to delete old photo.', 'error')

    try:
        db.execute("DELETE FROM students WHERE id = ?", (index,))
        db.commit()
        flash('Student data deleted successfully!', 'success')
    except sqlite3.Error as e:
        db.rollback()
        flash(f'An error occurred while deleting data: {e}', 'error')
    finally:
        db.close()

    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or len(username) < 3:
            flash('Username must be at least 3 characters', 'error')
            return redirect(url_for('register'))

        if not password or len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        db = get_db()
        try:
            if db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone():
                flash('Username already taken', 'error')
                return redirect(url_for('register'))

            password_hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            db.commit()
            flash('Registration successful. Please Login', 'success')
            return redirect(url_for('login'))
        except sqlite3.Error as e:
            db.rollback()
            flash(f'Error during registration: {e}', 'error')
        finally:
            db.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required', 'error')
            return redirect(url_for('login'))

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if user:
            reset_token = secrets.token_urlsafe(32)
            expiry = datetime.now() + timedelta(hours=1)  

            try:
                db.execute("UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE id = ?",
                        (reset_token, expiry, user['id']))
                db.commit()
                flash('A password reset link has been sent to your email.', 'success')
                return redirect(url_for('login'))  
            except sqlite3.Error as e:
                db.rollback()
                flash(f'Error creating reset token: {e}', 'error')
        else:
            flash('Username does not exist', 'error')  
        db.close()

    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE reset_token = ? AND reset_token_expiry > ?",
                    (token, datetime.now())).fetchone()

    if not user:
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if not new_password or len(new_password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('reset_password', token=token))

        new_password_hash = generate_password_hash(new_password)
        try:
            db.execute("UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL WHERE id = ?",
                    (new_password_hash, user['id']))
            db.commit()
            flash('Your password has been reset, you can log in now', 'success')
            return redirect(url_for('login'))  
        except sqlite3.Error as e:
            db.rollback()
            flash(f'Error during password update {e}', 'error')
        finally:
            db.close()

    return render_template('reset_password.html', token=token)


if __name__ == '__main__':
    app.run(debug=True)
