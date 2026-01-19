import frappe

def check_requirements():
    report = []
    
    # 1. Customer KYC
    customer_meta = frappe.get_meta("Customer")
    kyc_fields = ["pan", "aadhaar", "nominee", "date_of_birth"] # checking standard or custom
    missing_kyc = [f for f in kyc_fields if not customer_meta.get_field(f) and not customer_meta.get_field("custom_" + f)]
    report.append(f"1. Customer KYC Missing: {missing_kyc}")

    # 2. Vehicle
    if frappe.db.exists("DocType", "Vehicle"):
        vehicle_meta = frappe.get_meta("Vehicle")
        vehicle_fields = ["license_plate", "make", "model", "chassis_no", "engine_no"]
        missing_vehicle = [f for f in vehicle_fields if not vehicle_meta.get_field(f) and not vehicle_meta.get_field("custom_" + f)]
        report.append(f"2. Vehicle Fields Missing: {missing_vehicle}")
    else:
        report.append("2. Vehicle DocType Missing!")

    # 3. Product Config
    if not frappe.db.exists("DocType", "Insurance Plan"):
        report.append("3. Insurance Plan (Product) DocType Missing!")
    else:
        report.append("3. Insurance Plan exists (mapped to Insurance Product).")

    # 4. Endorsements
    if not frappe.db.exists("DocType", "Policy Endorsement"):
        report.append("4. Policy Endorsement DocType MISSING (Critical).")
    else:
        report.append("4. Policy Endorsement exists.")

    # 5. Renewals
    # Check for scheduled job/settings
    report.append("5. Renewal Logic: Needs background job verification.")

    print("\n".join(report))

if __name__ == "__main__":
    check_requirements()
