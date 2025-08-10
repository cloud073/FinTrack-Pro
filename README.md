# 📊 FinTrack Pro — Personal Finance Tracker

FinTrack Pro is a **full-stack personal finance tracker** that lets you securely register, log in, upload bank transaction CSV files, categorize expenses automatically, view history, generate summaries, and manage all your transactions — right from a modern web interface.

🚀 **Live Demo:** [sonisles.com](https://sonisles.com)  
*(Backend API hosted on Render, Frontend on Vercel)*

---

## ✨ Features

### 🔐 Authentication
- Secure user **registration** and **login** with hashed passwords.
- **JWT-based authentication** for secure API access.

### 📁 CSV Upload & Auto Categorization
- Upload CSV files with **`Date, Description, Amount`** columns.
- Automatically assigns **categories** using the `predict_category` model.
- Handles large CSVs (10,000+ entries) with **chunked database inserts**.

### 📜 Transaction Management
- View **paginated** transaction history.
- **Delete** individual transactions or clear all in one click.
- Fully supports **filtering & searching** on the frontend.

### 📈 Summary & Analytics
- View **category-wise spending summary**.
- Easy integration with **charts** for visual analytics.

---

## 🛠️ Tech Stack

### **Backend (Flask API)**
- **Flask** — Python micro-framework.
- **Flask-SQLAlchemy** — ORM for database management.
- **PostgreSQL** — Production database (via Render).
- **Flask-Bcrypt** — Password hashing.
- **PyJWT** — JWT-based authentication.
- **pandas** — CSV parsing.
- **gunicorn** — Production WSGI server.

### **Frontend**
- **React.js** — Modern SPA framework.
- **Axios** — HTTP requests.
- **TailwindCSS** — Styling.

### **Hosting**
- **Backend**: Render (API server)
- **Frontend**: Vercel
- **Database**: PostgreSQL (Render)

---

## 📂 Project Structure

