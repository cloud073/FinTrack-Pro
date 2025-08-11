from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import jwt
from functools import wraps
from sqlalchemy import or_
from categorizer import predict_category
from dotenv import load_dotenv
import os
import tempfile

# --- App & Config ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"])

# Load variables from .env file (useful locally; Render uses env vars)
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
DATABASE_URL = os.getenv("DATABASE_URL", None)

app.config["SECRET_KEY"] = SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Allow large uploads (example: 200 MB). Adjust as needed.
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- Models ---
class User(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(13, 2))
    category = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# --- JWT Decorator ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if not token:
            return jsonify({"error": "Token missing"}), 401
        try:
            if token.startswith("Bearer "):
                token = token.split(" ", 1)[1]
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(decoded['user_id'])
            if not current_user:
                return jsonify({"error": "User not found"}), 401
        except Exception:
            app.logger.exception("Token decode/validation error")
            return jsonify({"error": "Invalid or expired token"}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# --- Auth Routes ---
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400

    user = User(username=data['username'], email=data.get('email'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter(
        or_(User.username == data['username'], User.email == data['username'])
    ).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=4)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token})

# --- Health Check ---
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from Flask!"})

# --- Upload CSV (chunked / streaming) ---
@app.route('/api/upload-csv', methods=['POST'])
@token_required
def upload_csv(current_user):
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file name"}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
    except Exception:
        app.logger.exception("Failed to write uploaded file to temp")
        return jsonify({"error": "Failed to process uploaded file"}), 500

    required_columns = ['Date', 'Description', 'Amount']
    transactions_response = []

    try:
        chunk_iter = pd.read_csv(
            tmp_path,
            chunksize=200,
            iterator=True,
            dtype=str,
            usecols=required_columns
        )
    except Exception:
        try:
            chunk_iter = pd.read_csv(
                tmp_path,
                chunksize=200,
                iterator=True,
                encoding='ISO-8859-1',
                dtype=str,
                usecols=required_columns
            )
        except Exception:
            app.logger.exception("Failed to open CSV in any encoding")
            return jsonify({"error": "Failed to read CSV file"}), 400

    total_inserted = 0
    failed_rows = 0
    bulk_batch = []
    BATCH_SIZE = 1000

    try:
        for chunk in chunk_iter:
            if not all(col in chunk.columns for col in required_columns):
                return jsonify({"error": f"CSV must contain columns: {', '.join(required_columns)}"}), 400

            for row in chunk.itertuples(index=False):
                try:
                    date_obj = pd.to_datetime(row.Date, errors='coerce')
                    if pd.isnull(date_obj):
                        raise ValueError("Invalid date")
                    date_obj = date_obj.date()

                    description = str(row.Description).strip()

                    raw_amount = str(row.Amount).replace(',', '').replace('$', '').strip()
                    amount = float(raw_amount) if raw_amount else 0.0

                    category = predict_category(description)

                    txn = Transaction(
                        user_id=current_user.id,
                        date=date_obj,
                        description=description,
                        amount=amount,
                        category=category
                    )
                    bulk_batch.append(txn)

                    if len(transactions_response) < 10:
                        transactions_response.append({
                            "date": str(date_obj),
                            "description": description,
                            "amount": amount,
                            "category": category
                        })

                    if len(bulk_batch) >= BATCH_SIZE:
                        db.session.bulk_save_objects(bulk_batch)
                        db.session.commit()
                        total_inserted += len(bulk_batch)
                        bulk_batch = []

                except Exception:
                    failed_rows += 1
                    app.logger.exception("Skipping bad row")
                    continue

        if bulk_batch:
            db.session.bulk_save_objects(bulk_batch)
            db.session.commit()
            total_inserted += len(bulk_batch)

    except Exception:
        app.logger.exception("Error while processing CSV chunks")
        return jsonify({"error": "Error processing the CSV file"}), 500
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    return jsonify({
        "message": "CSV processed",
        "inserted": total_inserted,
        "failed_rows": failed_rows,
        "sample": transactions_response
    }), 200

# --- History ---
@app.route('/api/history', methods=['GET'])
@token_required
def get_history(current_user):
    page = request.args.get('page', 1, type=int)
    limit_param = request.args.get('limit', '1000')

    query = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc())

    if limit_param.lower() != 'all':
        try:
            per_page = int(limit_param)
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            items = paginated.items
        except ValueError:
            return jsonify({"error": "Invalid limit value"}), 400
    else:
        items = query.all()

    result = [{
        "id": txn.id,
        "date": txn.date.strftime("%Y-%m-%d"),
        "description": txn.description,
        "amount": float(txn.amount),
        "category": txn.category
    } for txn in items]

    return jsonify({
        "transactions": result,
        "total": len(result),
        "page": page,
        "pages": 1
    })

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
        summary_data = [{"category": cat, "total": float(total)} for cat, total in results]
        return jsonify({"summary": summary_data}), 200
    except Exception:
        app.logger.exception("Summary generation failed")
        return jsonify({"error": "Failed to generate summary"}), 500

# --- Delete Transaction ---
@app.route('/api/delete-transaction/<int:txn_id>', methods=['DELETE'])
@token_required
def delete_transaction(current_user, txn_id):
    txn = Transaction.query.filter_by(id=txn_id, user_id=current_user.id).first()
    if not txn:
        return jsonify({'error': 'Transaction not found'}), 404
    db.session.delete(txn)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted successfully'})

# --- Delete All Transactions ---
@app.route('/api/delete-all-transactions', methods=['DELETE'])
@token_required
def delete_all_transactions(current_user):
    deleted = Transaction.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'message': f'{deleted} transactions deleted successfully'})

# --- Ensure DB tables exist on startup ---
with app.app_context():
    db.create_all()

# --- Run Server ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT", 5000)))
