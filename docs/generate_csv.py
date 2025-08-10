import csv
import random
import os
from datetime import datetime, timedelta

# Save path and settings
save_path = "/home/vinit-soni/Desktop/PROJECTS/FinTrack-Pro/docs"
file_name = "sample10k.csv"
num_rows = 10000
full_path = os.path.join(save_path, file_name)

# Category → relevant descriptions
category_map = {
    "Groceries": ["Big Bazaar", "DMart", "Reliance Fresh", "Local Kirana Store"],
    "Utilities": ["Tata Power", "Adani Electricity", "BSES Rajdhani"],
    "Rent": ["Monthly Rent - Mr. Sharma", "PG Rent - Happy Homes"],
    "Transportation": ["Uber Ride", "Ola Ride", "Redbus", "IRCTC Ticket"],
    "Fuel": ["Indian Oil Petrol Pump", "Bharat Petroleum", "HP Petrol Pump"],
    "Dining": ["Zomato", "Swiggy", "Domino's", "Pizza Hut", "Cafe Coffee Day"],
    "Mobile Recharge": ["Jio Recharge", "Airtel Recharge", "BSNL Recharge"],
    "Electricity": ["BSES Bill Payment", "Tata Power Bill"],
    "Water Bill": ["Delhi Jal Board", "Bangalore Water Supply"],
    "Internet": ["Airtel Broadband", "JioFiber", "ACT Fibernet"],
    "DTH": ["Tata Sky", "DishTV", "Airtel DTH"],
    "Health": ["Hospital Fee", "Doctor Consultation", "Diagnostic Lab"],
    "Medicines": ["Apollo Pharmacy", "MedPlus", "1mg"],
    "Insurance": ["LIC Premium", "HDFC Life", "SBI General Insurance"],
    "Clothing": ["Shoppers Stop", "Pantaloons", "Zara", "H&M"],
    "Travel": ["MakeMyTrip", "Yatra", "Cleartrip", "IRCTC"],
    "Hotel": ["OYO Rooms", "Taj Hotels", "ITC Hotels"],
    "Education": ["School Fee - DPS", "College Fee - XYZ University"],
    "Tuition": ["Tuition Fee - Maths", "Tuition Fee - Science"],
    "Gym": ["Gold's Gym", "Cult Fit", "Anytime Fitness"],
    "Entertainment": ["Movie Ticket - PVR", "INOX", "Netflix Subscription"],
    "Streaming": ["Amazon Prime", "Disney+ Hotstar", "Sony LIV"],
    "Credit Card": ["HDFC Credit Card Bill", "SBI Card Payment"],
    "Loan EMI": ["HDFC Home Loan", "Axis Bank Car Loan EMI"],
    "Shopping": ["Amazon", "Flipkart", "Myntra"],
    "Household": ["Home Centre", "IKEA", "Croma"],
    "Donations": ["Donation to NGO", "Temple Donation", "Charity Trust"],
    "Petrol": ["Indian Oil", "Bharat Petroleum", "HP Petrol Pump"],
    "Snacks": ["Haldiram's", "Bikanervala", "Lays Chips"],
    "Electronics": ["Samsung Store", "Apple Store", "Croma", "Vijay Sales"]
}

# Date generator
def random_date():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    return (start_date + timedelta(days=random.randint(0, 180))).strftime('%Y-%m-%d')

# Write CSV without category names in description
with open(full_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Date", "Description", "Amount"])
    
    for _ in range(num_rows):
        category = random.choice(list(category_map.keys()))
        description = random.choice(category_map[category])  # No category prefix
        amount = round(random.uniform(50, 10000), 2)
        writer.writerow([random_date(), description, amount])

print(f"✅ Generated {num_rows} rows and saved as:\n📄 {full_path}")
