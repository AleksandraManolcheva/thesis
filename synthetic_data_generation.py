from faker import Faker
from pymongo import MongoClient
import random
from datetime import datetime
from app import HealthInsuranceEligibility  

fake = Faker('en_US')
client = MongoClient("mongodb://localhost:27017/")
db = client['health_insurance_db']
collection = db['eligibility_data_']

states = [
    "California", "Texas", "Florida", "New York", "Pennsylvania", "Illinois", "Ohio",
    "Georgia", "North Carolina", "New Jersey", "Virginia", "Washington",
    "Arizona", "Massachusetts", "Tennessee", "Indiana", "Missouri", "Maryland", "Wisconsin",
    "Colorado", "South Carolina", "Alabama", "Louisiana", "Kentucky", "Oregon",
    "Oklahoma", "Connecticut", "Iowa", "Mississippi", "Arkansas", "Kansas", "Utah", "Nevada",
    "New Mexico", "Nebraska", "West Virginia", "Idaho", "Hawaii", "Maine", "Montana", "Rhode Island",
    "Delaware", "South Dakota", "North Dakota", "Alaska", "Vermont", "Wyoming", "District of Columbia"
]

disability_chance = 0.1  # 10% chance someone has a disability

def generate_fake_person():
    family_size = random.randint(1, 5)
    ages = [random.randint(0, 90) for _ in range(family_size)]
    disabilities = [random.random() < disability_chance for _ in range(family_size)]
    medical_necessity = [random.choice([True, False]) for _ in range(family_size)]

    income = random.randint(10000, 90000)
    expenses = {
        "passive": round(random.uniform(500, 3000), 2),
        "active": round(random.uniform(500, 3000), 2)
    }
    state = random.choice(states)
    location = random.choice(["urban", "rural"])
    citizenship_status = random.choice(["U.S. citizen", "Non-U.S. citizen"])
    residency_status = random.choice(["State resident", "Non-state resident"])

    eligibility_checker = HealthInsuranceEligibility(
        income=income,
        family_size=family_size,
        ages=ages,
        state=state,
        citizenship_status=citizenship_status,
        residency_status=residency_status,
        medical_necessity=medical_necessity,
        disability=disabilities,
        expenses=expenses
    )

    eligibility_summary = eligibility_checker.eligibility_summary()

    provider_incentive = {
        "provider_id": random.randint(1, 10),
        "location": location,
        "specialty": random.choice(["general", "specialist"]),
        "incentive": "Standard incentive + High patient satisfaction bonus"
    }

    claim_type = random.choice(["routine", "urgent"])
    coverage = "Full coverage for routine care." if "Eligible" in eligibility_summary["Medicaid"] else "Coverage denied."
    claim_status = {
        "patient_id": fake.random_int(min=100, max=999),
        "status": "Pending",
        "claim_type": claim_type,
        "coverage": coverage
    }

    visit_data = "Routine check-up provided. No immediate concerns." if "Eligible" in eligibility_summary["Medicaid"] else "Visit advised based on healthcare needs."

    doc = {
        "eligibility_summary": eligibility_summary,
        "visit_data": visit_data,
        "provider_incentives": [provider_incentive],
        "claims_status": [claim_status],
        "input_parameters": {
            "income": income,
            "family_size": family_size,
            "ages": ages,
            "state": state,
            "citizenship_status": citizenship_status,
            "residency_status": residency_status,
            "medical_necessity": medical_necessity,
            "disability": disabilities,
            "expenses": expenses,
            "location": location
        },
        "timestamp": datetime.utcnow()
    }

    return doc

for _ in range(1000000):  # ⚡ Make sure Mongo can handle 1M records — can reduce for testing
    collection.insert_one(generate_fake_person())

print("✅ Sample data inserted into MongoDB (eligibility_data_)!")
