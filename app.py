from flask import Flask, render_template, request
from pymongo import MongoClient
import datetime

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["health_insurance_db"]
collection = db["eligibility_data_"]

# Health Insurance Eligibility Class
class HealthInsuranceEligibility:
    def __init__(self, income, family_size, ages, state, citizenship_status, residency_status, medical_necessity, disability, expenses):
        self.income = income
        self.family_size = family_size
        self.ages = ages
        self.state = state.title()
        self.citizenship_status = citizenship_status
        self.residency_status = residency_status
        self.medical_necessity = medical_necessity
        self.disability = disability
        self.expenses = expenses
        self.fpl = self.get_federal_poverty_level()
        self.state_specific_thresholds = self.get_state_thresholds()

    def get_federal_poverty_level(self):
        fpl_2024 = {
            "default": {1: 15060, 2: 20340, 3: 25620, 4: 30900, 5: 36180, 6: 41460},
            "Hawaii": {1: 17310, 2: 23390, 3: 29470, 4: 35550, 5: 41630, 6: 47710},
            "Alaska": {1: 18890, 2: 25550, 3: 32210, 4: 38870, 5: 45530, 6: 52190}
        }
        if self.state == "Hawaii":
            base_fpl = fpl_2024["Hawaii"]
        elif self.state == "Alaska":
            base_fpl = fpl_2024["Alaska"]
        else:
            base_fpl = fpl_2024["default"]
        if self.family_size <= 6:
            return base_fpl[self.family_size]
        else:
            additional = 5250 if self.state != "Hawaii" and self.state != "Alaska" else (6060 if self.state == "Hawaii" else 6730)
            return base_fpl[6] + additional * (self.family_size - 6)

    def get_state_thresholds(self):
        thresholds = {
            "Texas": {"medicaid": 138, "chip": 300},
            "California": {"medicaid": 138, "chip": 250},
            "New York": {"medicaid": 150, "chip": 400},
        }
        return thresholds.get(self.state, {"medicaid": 138, "chip": 300})

    def check_medicaid_eligibility(self):
        if self.income < (self.fpl * self.state_specific_thresholds["medicaid"] / 100):
            eligible_members = [
                age for idx, age in enumerate(self.ages)
                if age < 19 or age >= 65 or self.disability[idx] or self.medical_necessity[idx]
            ]
            return f"Eligible for Medicaid for members: {eligible_members}" if eligible_members else "Not eligible for Medicaid."
        return "Not eligible for Medicaid."

    def check_chip_eligibility(self):
        if self.income < (self.fpl * self.state_specific_thresholds["chip"] / 100):
            eligible_members = [age for age in self.ages if age < 19]
            return f"Eligible for CHIP for members: {eligible_members}" if eligible_members else "Not eligible for CHIP."
        return "Not eligible for CHIP."

    def check_marketplace_eligibility(self):
        if self.income < (self.fpl * 100 / 100):
            return "Not eligible for marketplace coverage. Consider Medicaid."
        elif self.income <= (self.fpl * 400 / 100):
            eligible_members = [age for age in self.ages if age >= 18]
            return f"Eligible for marketplace coverage with potential premium tax credits for members: {eligible_members}"
        else:
            return "Eligible for marketplace coverage but may not qualify for premium tax credits."

    def check_medicare_eligibility(self):
        eligible_members = [age for i, age in enumerate(self.ages) if age >= 65 or self.disability[i]]
        return f"Eligible for Medicare for members: {eligible_members}" if eligible_members else "Not eligible for Medicare."

    def eligibility_summary(self):
        return {
            "Medicaid": self.check_medicaid_eligibility(),
            "CHIP": self.check_chip_eligibility(),
            "Marketplace": self.check_marketplace_eligibility(),
            "Medicare": self.check_medicare_eligibility(),
        }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        income = float(request.form['income'])
        family_size = int(request.form['family_size'])
        ages = list(map(int, request.form['ages'].split(',')))
        state = request.form['state']
        citizenship_status = request.form['citizenship_status']
        residency_status = request.form['residency_status']
        medical_necessity = list(map(int, request.form['medical_necessity'].split(',')))
        disability = list(map(int, request.form['disability'].split(',')))
        expenses = {
            "passive": float(request.form['passive_expenses']),
            "active": float(request.form['active_expenses'])
        }

        # Personal info and contact fields
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        ssn = request.form['ssn']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']

        eligibility_checker = HealthInsuranceEligibility(
            income, family_size, ages, state, citizenship_status, residency_status,
            medical_necessity, disability, expenses
        )

        eligibility = eligibility_checker.eligibility_summary()

       
        document = {
            "eligibility_summary": eligibility,
            "visit_data": "Routine check-up provided. No immediate concerns.",
            "provider_incentives": [
                {
                    "provider_id": 2,
                    "location": "urban",
                    "specialty": "general",
                    "incentive": "Standard incentive + High patient satisfaction bonus"
                }
            ],
            "claims_status": [
                {
                    "patient_id": 101,
                    "status": "Pending",
                    "claim_type": "routine",
                    "coverage": "Full coverage for routine care."
                }
            ],
            "input_parameters": {
                "income": income,
                "family_size": family_size,
                "ages": ages,
                "state": state,
                "citizenship_status": citizenship_status,
                "residency_status": residency_status,
                "medical_necessity": medical_necessity,
                "disability": disability,
                "expenses": expenses,
                "location": "urban"
            },
            "personal_info": {
                "first_name": first_name,
                "last_name": last_name,
                "dob": dob,
                "ssn": ssn
            },
            "contact": {
                "phone": phone,
                "email": email,
                "address": address
            },
            "timestamp": datetime.datetime.now()
        }

        # Insert into MongoDB
        collection.insert_one(document)

        return render_template('index.html', eligibility=eligibility)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
