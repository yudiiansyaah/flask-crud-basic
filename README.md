# 🎓 Flask Student Management Application

A modern web application built with Flask to manage student records efficiently. Features CRUD operations, user authentication, and secure photo uploads. 

![Flask](https://img.shields.io/badge/Flask-2.0.1-%23000.svg?logo=flask)
![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📸 Screenshots

| **Home** | **Edit Student** | **Login** |
|----------|------------------|-----------|
| ![Home](static/uploads/home.png) | ![Edit](static/uploads/edit.png) | ![Login](static/uploads/login.png) |

| **Register** | **Forgot Password** |
|--------------|---------------------|
| ![Register](static/uploads/register.png) | ![Forgot](static/uploads/forgot.png) |

## ✨ Features

### 🧑🎓 Student Management
- **Add** new students with name, age, and profile photo
- **View** all students in a clean table layout
- **Edit** existing student information
- **Delete** student records permanently

### 🔐 User Authentication
- Secure **user registration** with email validation
- **Login/Logout** functionality with session management
- **Password reset** via token-based email system
- Password hashing using **bcrypt**

### 🖼️ Media Handling
- Upload student photos (JPG/JPEG/PNG, max 2MB)
- Automatic image thumbnail generation
- Secure file storage in `static/uploads`

### 🛡️ Security
- CSRF protection for all forms
- SQLite database with parameterized queries
- Session-based authentication

## 🚀 Quick Start

### Prerequisites
- Python 3.6+
- pip package manager

### Installation
1. **Clone repository**
   ```bash
   git clone https://github.com/yudiiansyaah/flask-crud-basic.git
   cd flask-crud-basic

2.  **Create a Virtual Environment (Recommended):**

    ```bash
    python -m venv venv
    ```
     *   **Activate the virtual environment:**
    *   **macOS/Linux:**
    ```bash
        source venv/bin/activate
    ```
     *   **Windows:**
    ```bash
        venv\Scripts\activate
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Application:**

    ```bash
    python app.py
    ```
    (Optional: To run with debugging enabled, use `python app.py --debug`)

5.  **Access the Application:**
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Database Setup

The application uses SQLite to store data. The database file `siswa.db` is created automatically in the same directory as your `app.py`. The database will be automatically initialized with the `students` and `users` tables.

## Usage

1.  **Register or Login:** To access the application's features, you will need to register or login using the link at the login page.
2.  **Manage Students:** Once logged in, use the links on the navbar to add new student records, view the existing list, and edit or delete records as necessary.
3.  **Password Reset:** If you forget your password, use the "Forgot Password" link on the login page to request a password reset link.

## Project Structure
```
flask-crud-basic/
├── app.py                 # Main application entry
├── siswa.db               # SQLite database
├── requirements.txt       # Dependencies
├── static/
│   ├── uploads/           # Student photos storage
│   └── style.css          # Custom CSS styles
└── templates/
    ├── base.html          # Master template
    ├── index.html         # Student listing
    ├── {add,update}.html  # CRUD operations
    └── auth/              # Authentication templates
        ├── login.html
        ├── register.html
        └── password_reset/
            ├── forgot.html
            └── reset.html
```


## Contributing

Feel free to fork this repository and submit pull requests with improvements or bug fixes.

## License

This project is open source. Feel free to modify and use it as you like.
