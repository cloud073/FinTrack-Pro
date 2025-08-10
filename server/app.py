# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import jwt
from functools import wraps
from sqlalchemy import or_
from categorizer import predict_category     # keep your existing categorizer
from dotenv import load_dotenv
import os
import math
import tempfile

# --- App & Config ---
app = Flask(__name__)

# Allow CORS only for API routes (adjust origin in production)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Load environment variables from .env (or from environment in production)
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or "super-secret-default"   # replace in prod via env
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///fintrack.db"  # fallback to sqlite for dev

# App config
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Allow larger uploads (e.g. 50 MB). Adjust depending on host limits.
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- Models ---
class User(db.Model):
    __tablename__ = "users"   # explicit table name avoids reserved-word issues
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(12, 2))
    category = db.Column(db.String(100), index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# --- JWT Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(decoded['user_id'])
            if not current_user:
                return jsonify({"error": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except Exception as e:
            app.logger.exception("Token decode error")
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# --- Auth Routes ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "username and password required"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(username=data['username'], email=data.get('email'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "username and password required"}), 400

    user = User.query.filter(
        or_(User.username == data['username'], User.email == data['username'])
    ).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=6)   # longer token for usability
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})

# --- Health Check ---
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from Flask!"})

# --- Upload CSV ---
@app.route('/api/upload-csv', methods=['POST'])
@token_required
def upload_csv(current_user):
    """
    1) Accept file upload
    2) Read via pandas (with encoding fallback)
    3) Validate columns
    4) Create Transaction objects and bulk insert in chunks
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file name"}), 400

    # Save temporarily in case pandas needs to reopen the file
    try:
        tmp = tempfile.NamedTemporaryFile(delete=False)
        file.save(tmp.name)
        tmp.flush()
    except Exception as e:
        app.logger.exception("Failed to save uploaded file")
        return jsonify({"error": "Failed to save uploaded file"}), 500

    try:
        try:
            df = pd.read_csv(tmp.name)
        except UnicodeDecodeError:
            df = pd.read_csv(tmp.name, encoding='ISO-8859-1')
        except Exception as e:
            app.logger.exception("pandas read_csv error")
            return jsonify({"error": "Failed to parse CSV file"}), 400

        required_columns = ['Date', 'Description', 'Amount']
        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": f"CSV must contain columns: {', '.join(required_columns)}"}), 400

        transactions_to_insert = []
        preview_list = []

        # iterate rows (vectorized methods might be faster but we need category per description)
        for idx, row in df.iterrows():
            try:
                # Robust date parsing
                date_obj = pd.to_datetime(row['Date'], errors='coerce')
                if pd.isna(date_obj):
                    # skip rows with invalid date
                    app.logger.debug(f"Skipping row {idx}: invalid date -> {row.get('Date')}")
                    continue
                date_obj = date_obj.date()

                description = str(row['Description']) if not pd.isna(row['Description']) else ""
                amount = float(row['Amount']) if pd.notnull(row['Amount']) else 0.0

                # run your categorizer
                try:
                    category = predict_category(description)
                except Exception:
                    category = "Uncategorized"

                transactions_to_insert.append(Transaction(
                    user_id=current_user.id,
                    date=date_obj,
                    description=description,
                    amount=amount,
                    category=category
                ))

                # small preview to return to frontend
                preview_list.append({
                    "date": str(date_obj),
                    "description": description,
                    "amount": amount,
                    "category": category
                })
            except Exception as e:
                app.logger.exception("Skipping row due to error")
                continue

        # Insert in chunks to avoid long single transactions / memory spikes.
        chunk_size = 1000
        total = len(transactions_to_insert)
        if total > 0:
            for i in range(0, total, chunk_size):
                chunk = transactions_to_insert[i:i+chunk_size]
                db.session.bulk_save_objects(chunk)
                db.session.commit()

        return jsonify({"transactions": preview_list, "inserted": total}), 200

    except Exception as e:
        app.logger.exception("Error processing upload")
        return jsonify({"error": "Error processing the file"}), 500
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass

# --- History ---
@app.route('/api/history', methods=['GET'])
@token_required
def get_history(current_user):
    """
    Query params:
      - page (int) : page number for pagination (default 1)
      - limit (int | 'all') : number per page or 'all'
      - category (str) optional filter by category
    """
    page = request.args.get('page', 1, type=int)
    limit_param = request.args.get('limit', '1000')
    category_filter = request.args.get('category', None)

    query = Transaction.query.filter_by(user_id=current_user.id)

    if category_filter:
        query = query.filter(Transaction.category == category_filter)

    query = query.order_by(Transaction.date.desc())

    if isinstance(limit_param, str) and limit_param.lower() == 'all':
        items = query.all()
        total = len(items)
        pages = 1
    else:
        try:
            per_page = int(limit_param)
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            items = paginated.items
            total = paginated.total
            pages = paginated.pages
        except ValueError:
            return jsonify({"error": "Invalid limit value"}), 400

    result = [{
        "id": txn.id,
        "date": txn.date.strftime("%Y-%m-%d"),
        "description": txn.description,
        "amount": float(txn.amount),
        "category": txn.category
    } for txn in items]

    return jsonify({
        "transactions": result,
        "total": total,
        "page": page,
        "pages": pages
    }), 200

# --- Summary ---
@app.route('/api/summary', methods=['GET'])
@token_required
def summary(current_user):
    try:
        results = (
            db.session.query(Transaction.category, db.func.sum(Transaction.amount))
            .filter(Transaction.user_id == current_user.id)
            .group_by(Transaction.category)
            .all()
        )
        summary_data = [{"category": cat if cat else "Uncategorized", "total": float(total)} for cat, total in results]
        return jsonify({"summary": summary_data}), 200
    except Exception as e:
        app.logger.exception("Failed to generate summary")
        return jsonify({"error": "Failed to generate summary"}), 500

# --- Delete Single Transaction ---
@app.route('/api/delete-transaction/<int:txn_id>', methods=['DELETE'])
@token_required
def delete_transaction(current_user, txn_id):
    txn = Transaction.query.filter_by(id=txn_id, user_id=current_user.id).first()
    if not txn:
        return jsonify({'error': 'Transaction not found'}), 404
    db.session.delete(txn)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted successfully'}), 200

# --- Delete All Transactions ---
@app.route('/api/delete-all-transactions', methods=['DELETE'])
@token_required
def delete_all_transactions(current_user):
    deleted = Transaction.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'message': f'{deleted} transactions deleted successfully'}), 200

# --- Ensure DB tables exist on every startup ---
with app.app_context():
    db.create_all()

# --- Run Server (development) ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
