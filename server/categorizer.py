# categorizer.py
import os
import joblib
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "model.pkl"

# Expanded & Indianized dataset
SAMPLES = [
    # --- Food ---
    ("Swiggy Order", "Food"),
    ("Zomato Food Delivery", "Food"),
    ("Domino's Pizza", "Food"),
    ("McDonald's India", "Food"),
    ("Cafe Coffee Day", "Food"),
    ("Starbucks Coffee", "Food"),
    ("Subway India", "Food"),
    ("Burger King meal", "Food"),
    ("OvenStory Pizza", "Food"),
    ("Barbeque Nation Buffet", "Food"),
    ("Street food vendor UPI", "Food"),
    ("Lunch at highway dhaba", "Food"),

    # --- Shopping ---
    ("Amazon Purchase", "Shopping"),
    ("Flipkart Electronics", "Shopping"),
    ("Myntra Fashion", "Shopping"),
    ("Ajio Order", "Shopping"),
    ("Big Bazaar Groceries", "Shopping"),
    ("Croma Electronics", "Shopping"),
    ("Snapdeal Wallet", "Shopping"),
    ("DMart Payment", "Shopping"),
    ("Reliance Digital", "Shopping"),
    ("Spencer’s Retail", "Shopping"),
    ("Nykaa Cosmetics", "Shopping"),
    ("Lenskart payment", "Shopping"),

    # --- Transport ---
    ("Uber Ride", "Transport"),
    ("Ola Cabs", "Transport"),
    ("Petrol Bunk IOCL", "Transport"),
    ("Indian Oil Fuel Pump", "Transport"),
    ("Bharat Petroleum refill", "Transport"),
    ("Metro Recharge Card", "Transport"),
    ("Redbus Booking", "Transport"),
    ("Train IRCTC", "Transport"),
    ("Uber Auto", "Transport"),
    ("Taxi fare", "Transport"),
    ("FASTag toll", "Transport"),

    # --- Utilities ---
    ("TNEB Electricity Bill", "Utilities"),
    ("BWSSB Water Payment", "Utilities"),
    ("Airtel Postpaid", "Utilities"),
    ("Vodafone Idea Recharge", "Utilities"),
    ("Jio Fiber Bill", "Utilities"),
    ("Gas Refill Indane", "Utilities"),
    ("HP Gas Booking", "Utilities"),
    ("Tata Sky DTH", "Utilities"),
    ("ACT Broadband", "Utilities"),
    ("Mobile Recharge Paytm", "Utilities"),
    ("Jio Prepaid", "Utilities"),

    # --- Rent ---
    ("Rent paid via GPay", "Rent"),
    ("House rent transfer", "Rent"),
    ("Monthly rent landlord", "Rent"),
    ("UPI rent payment", "Rent"),
    ("Rent through PhonePe", "Rent"),

    # --- Entertainment ---
    ("Netflix India", "Entertainment"),
    ("Amazon Prime Video", "Entertainment"),
    ("Hotstar Subscription", "Entertainment"),
    ("BookMyShow Tickets", "Entertainment"),
    ("Spotify Premium", "Entertainment"),
    ("YouTube Premium", "Entertainment"),
    ("Gaming app recharge", "Entertainment"),
    ("ZEE5 Subscription", "Entertainment"),
    ("SonyLiv", "Entertainment"),
    ("Inox Cinema", "Entertainment"),

    # --- Health ---
    ("Apollo Pharmacy", "Health"),
    ("Doctor Visit", "Health"),
    ("Medical Reimbursement", "Health"),
    ("Practo Appointment", "Health"),
    ("Hospital Bill", "Health"),
    ("Pathology Lab Test", "Health"),
    ("Health Checkup Package", "Health"),
    ("1mg Medicine Order", "Health"),
    ("Eye checkup", "Health"),

    # --- Travel ---
    ("Flight ticket via Goibibo", "Travel"),
    ("Hotel Booking OYO", "Travel"),
    ("MakeMyTrip trip", "Travel"),
    ("Travel Insurance", "Travel"),
    ("Train ticket IRCTC", "Travel"),
    ("Bus fare via RedBus", "Travel"),
    ("Yatra hotel", "Travel"),
    ("Trip expense Uber", "Travel"),

    # --- Education ---
    ("Udemy course", "Education"),
    ("Unacademy Class", "Education"),
    ("Tuition Fees School", "Education"),
    ("Online course Coursera", "Education"),
    ("Books purchase", "Education"),
    ("College Admission Fee", "Education"),
    ("Byju's Subscription", "Education"),
    ("Offline Coaching Fee", "Education"),

    # --- Finance ---
    ("ATM Withdrawal", "Finance"),
    ("SBI Bank Charges", "Finance"),
    ("Credit card bill", "Finance"),
    ("Loan EMI Payment", "Finance"),
    ("Debit card annual fee", "Finance"),
    ("Wallet Load Paytm", "Finance"),
    ("NEFT Transfer", "Finance"),
    ("Cash Withdrawal", "Finance"),
    ("Overdraft Fee", "Finance"),

    # --- Investment ---
    ("SIP via Groww", "Investment"),
    ("Mutual Fund via Zerodha", "Investment"),
    ("Stocks investment", "Investment"),
    ("NPS contribution", "Investment"),
    ("FD Deposit", "Investment"),
    ("Smallcase investment", "Investment"),
    ("CoinSwitch investment", "Investment"),

    # --- Insurance ---
    ("LIC Premium", "Insurance"),
    ("Car Insurance Renewal", "Insurance"),
    ("Health Insurance MaxBupa", "Insurance"),
    ("Phone Insurance", "Insurance"),
    ("Bike Insurance Renewal", "Insurance"),
    ("Policybazaar Payment", "Insurance"),

    # --- Other ---
    ("UPI to friend", "Other"),
    ("Donation to NGO", "Other"),
    ("Income tax paid", "Other"),
    ("Freelance income", "Other"),
    ("Bank refund", "Other"),
    ("Gift card redemption", "Other"),
    ("Unknown UPI", "Other"),
    ("Cash deposit", "Other"),
    ("GPay received", "Other"),
]

def preprocess(text):
    # Lowercase and remove punctuation
    return text.lower().translate(str.maketrans('', '', string.punctuation))

def train_and_save_model():
    descriptions = [preprocess(x[0]) for x in SAMPLES]
    labels = [x[1] for x in SAMPLES]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english')
    X = vectorizer.fit_transform(descriptions)

    model = LogisticRegression(max_iter=1000)
    model.fit(X, labels)

    joblib.dump((vectorizer, model), MODEL_PATH)
    print("✅ Model trained and saved to", MODEL_PATH)

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise Exception("❌ ML model not trained. Run categorizer.py to train first.")
    return joblib.load(MODEL_PATH)

def predict_category(description):
    vec, clf = load_model()
    clean_desc = preprocess(description)
    x = vec.transform([clean_desc])
    return clf.predict(x)[0]

if __name__ == '__main__':
    train_and_save_model()
