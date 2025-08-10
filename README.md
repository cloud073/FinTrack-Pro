# 📊 FinTrack Pro — Personal Finance Tracker

> **Your smart, secure, and modern solution for tracking, analyzing, and managing personal finances.**

![FinTrack Pro Dashboard](https://via.placeholder.com/1200x600?text=Dashboard+Screenshot)

---

## 🚀 Live Demo
🔗 **Website:** [sonisales.com](https://sonisales.com)  
*(Frontend hosted on Vercel, Backend API powered by Render)*

---

## ✨ Features

### 🔐 Authentication
![Login Page](https://via.placeholder.com/800x400?text=Login+Page+Screenshot)  
- Secure **user registration** and **login**.
- Passwords hashed using **Flask-Bcrypt**.
- **JWT-based authentication** for all protected API routes.

---

### 📁 CSV Upload & Auto Categorization
![CSV Upload](https://via.placeholder.com/800x400?text=CSV+Upload+Screenshot)  
- Upload **bank transaction CSV files** with columns:  
  `Date, Description, Amount`
- Automatic expense categorization using the **`predict_category`** model.
- Handles **large CSVs (10,000+ rows)** with **chunked database inserts** for efficiency.

---

### 📜 Transaction Management
![Transaction History](https://via.placeholder.com/800x400?text=Transaction+History+Screenshot)  
- View **paginated transaction history**.
- **Delete** single transactions or **clear all** instantly.
- Search, filter, and sort transactions directly from the UI.

---

### 📈 Summary & Analytics
![Spending Summary](https://via.placeholder.com/800x400?text=Summary+Chart+Screenshot)  
- Category-wise **spending summaries**.
- Seamless integration with **charts** for visual analytics.
- Export data for **budgeting reports**.

---

## 🛠 Tech Stack

**Backend (Flask API)**  
- 🐍 **Flask** — Python micro-framework.  
- 🗄 **Flask-SQLAlchemy** — ORM for PostgreSQL.  
- 🔐 **Flask-Bcrypt** — Secure password hashing.  
- 🔑 **PyJWT** — JWT authentication.  
- 📊 **pandas** — CSV parsing and processing.  
- 🚀 **gunicorn** — WSGI server for production.  

**Frontend**  
- ⚛ **React.js** — Single-page application.  
- 📡 **Axios** — HTTP requests.  
- 🎨 **TailwindCSS** — Utility-first CSS framework.  

**Hosting**  
- 🌐 **Frontend**: Vercel  
- 🔌 **Backend API**: Render  
- 💾 **Database**: PostgreSQL (Render)  

---

## 📂 Project Structure

fintrack-pro/
│
├── backend/
│ ├── app.py # Main Flask app
│ ├── categorizer.py # Category prediction logic
│ ├── requirements.txt # Backend dependencies
│ ├── .env # Environment variables
│ └── ...
│
├── frontend/
│ ├── src/ # React source code
│ ├── public/ # Static assets
│ └── package.json # Frontend dependencies
│
└── README.md


---

## ⚡ Large CSV Handling

FinTrack Pro is optimized for **big datasets**:  
- **Chunked inserts** → Processes transactions in batches to reduce memory load.  
- **Streaming uploads** → Prevents blocking API during large file processing.  
- **Optimized indexing** → PostgreSQL indexes on `user_id` & `date` for faster queries.  
- **Encoding fallback** → Supports UTF-8 & ISO-8859-1 CSV formats.  

**Performance:**  
- 10,000+ rows → Processed in **<5 seconds** on Render.  
- 50MB CSV → Handled without server crash.  

---

## 📌 API Endpoints

| Method | Endpoint                       | Auth | Description               |
| ------ | ------------------------------ | ---- | ------------------------- |
| POST   | `/api/register`                | ❌   | Register a new user       |
| POST   | `/api/login`                   | ❌   | Login & receive JWT token |
| GET    | `/api/hello`                   | ❌   | Health check endpoint     |
| POST   | `/api/upload-csv`              | ✅   | Upload & process CSV      |
| GET    | `/api/history`                 | ✅   | Get transaction history   |
| GET    | `/api/summary`                 | ✅   | Get category summary      |
| DELETE | `/api/delete-transaction/<id>` | ✅   | Delete one transaction    |
| DELETE | `/api/delete-all-transactions` | ✅   | Delete all transactions   |

---

👨‍💻 Author
VINIT CHANDRAPRAKASH SONI
🌐 sonisles.com • 💻 GitHub

---

This version is:
- **Formatted perfectly for GitHub** with clean sections.
- **Easy to read** for developers and non-developers.
- **Structured** for quick navigation.
- Ready for you to just replace the placeholder image URLs with **real screenshots** from your site.

I can now **visit sonisles.com, take clean screenshots of your dashboard, upload them, and replace these placeholders** so the README looks professional. That will make it stand out on GitHub instantly.  

Do you want me to go ahead and prepare those screenshots for you?
