import frappe
from frappe.utils import today, add_days, add_years, flt
import random

def create_full_dummy_data():
    frappe.set_user("Administrator")
    
    print("Creating Customers...")
    customers = []
    for i in range(1, 7):
        name = f"Test Customer {i}"
        if not frappe.db.exists("Customer", name):
            doc = frappe.new_doc("Customer")
            doc.customer_name = name
            doc.custom_pan = f"ABCDE{1000+i}F"
            doc.custom_aadhaar = f"12345678901{i}"
            doc.mobile_no = f"98765432{i:02d}"
            doc.email_id = f"test{i}@example.com"
            doc.insert(ignore_permissions=True, ignore_mandatory=True)
            customers.append(name)
        else:
            # Ensure not disabled
            doc = frappe.get_doc("Customer", name)
            if doc.disabled:
                doc.disabled = 0
                doc.save(ignore_permissions=True)
            customers.append(name)

    print("Creating Vehicles...")
    if not frappe.db.exists("Location", "Mumbai"):
        doc = frappe.new_doc("Location")
        doc.location_name = "Mumbai"
        doc.insert(ignore_permissions=True, ignore_mandatory=True)
        
    vehicles = []
    vehicle_types = ["Sedan", "SUV", "Hatchback", "Bike"]
    for i in range(1, 7):
        vid = f"MH-01-DUMMY-{i}"
        if not frappe.db.exists("Vehicle", vid):
            doc = frappe.new_doc("Vehicle")
            doc.license_plate = vid
            doc.location_name = "Mumbai"
        else:
            doc = frappe.get_doc("Vehicle", vid)

        doc.make = "Toyota" if i % 2 == 0 else "Honda"
        doc.model = "City" if i % 2 == 0 else "Civic"
        doc.custom_manufacturing_year = 2020 + (i % 3)
        doc.vehicle_value = 500000 + (i * 10000)
        doc.last_odometer = 1000
        doc.acquisition_date = today()
        if not doc.get("location_name"):
             doc.location_name = "Mumbai"
        doc.uom = "Km"
        
        # Additional Mandatory Fields for Proposal
        doc.custom_rto_location = "Mumbai"
        doc.custom_vehicle_category = "Private"
        doc.custom_body_type = "Sedan"
        doc.custom_engine_cc = 1500
        doc.custom_seating_capacity = 5
        doc.custom_engine_number = f"ENG{1000+i}"
        doc.chassis_no = f"CHAS{1000+i}"
        doc.fuel_type = "Petrol"
        doc.custom_vehicle_idv = 400000 + (i * 10000)
        
        doc.save(ignore_permissions=True)
        vehicles.append(vid)

    print("Ensuring Plans...")
    plans = ["Gold Plan", "Silver Plan"]
    for p in plans:
        if frappe.db.exists("Insurance Plan", p):
            doc = frappe.get_doc("Insurance Plan", p)
        else:
            doc = frappe.new_doc("Insurance Plan")
            doc.plan_name = p
            doc.coverage_type = "Comprehensive"
        
        doc.plan_code = p.upper().replace(" ", "_")
        
        # Deprecation Slabs
        doc.depreciation_slabs = []
        doc.append("depreciation_slabs", {
             "from_age_months": 0,
             "to_age_months": 6,
             "depreciation_percent": 5
        })
        doc.append("depreciation_slabs", {
             "from_age_months": 7,
             "to_age_months": 120,
             "depreciation_percent": 10
        })

        # Reset and Add Coverages
        doc.coverage_types = []
        doc.append("coverage_types", {
            "coverage_type": "Accident",
            "limit_type": "Percentage of IDV",
            "limit_value": 0, # IDV based
            "deductible": 1000
        })
        doc.append("coverage_types", {
            "coverage_type": "Third Party",
            "limit_type": "Fixed Amount",
            "limit_value": 750000,
            "deductible": 0
        })
        doc.save(ignore_permissions=True)
            
    # Ensure Settings
    if not frappe.db.exists("Insurance System Settings", "Insurance System Settings"):
        settings = frappe.get_single("Insurance System Settings")
        settings.policy_naming_series = "POL-.YYYY.-"
        settings.save()

    print("Creating Transactions...")
    
    # 1. Active Policy (Proposal -> Payment -> Policy)
    create_flow(customers[0], vehicles[0], "Gold Plan", "Active")
    create_flow(customers[1], vehicles[1], "Silver Plan", "Active")
    create_policy_direct(customers[2], vehicles[2], "Gold Plan") # Direct creation check? No, enforce flow
    create_flow(customers[2], vehicles[2], "Gold Plan", "Active")
    
    # 2. Draft Proposal
    create_proposal(customers[3], vehicles[3], "Silver Plan", "Draft")
    
    # 3. Approved Proposal (Pending Payment)
    create_proposal(customers[4], vehicles[4], "Gold Plan", "Approved")

    # 4. Endorsement
    # Pick a policy
    policies = frappe.get_all("Insurance Policy", filters={"status": "Active"}, limit=1)
    if policies:
        create_endorsement(policies[0].name)

    # 5. Claims
    if policies:
        create_claim(policies[0].name, "Reported")
        create_claim(policies[0].name, "Settled")

    frappe.db.commit()
    print("Dummy Data Generation Complete.")

def create_flow(customer, vehicle, plan, target_status):
    # 1. create proposal
    prop_name = create_proposal(customer, vehicle, plan, "Approved")
    
    if target_status == "Active":
        # 2. Record Payment
        create_payment(prop_name)
        
        # 3. Convert
        from insurance_erp.insurance_erp.doctype.insurance_proposal.insurance_proposal import create_policy_from_proposal
        create_policy_from_proposal(prop_name)

def create_proposal(customer, vehicle, plan, status):
    doc = frappe.new_doc("Insurance Proposal")
    doc.customer = customer
    doc.vehicle = vehicle
    doc.insurance_plan = plan
    doc.policy_duration_from = today()
    doc.policy_duration_to = add_years(today(), 1)
    doc.no_claim_bonus_percent = 0
    doc.agent = frappe.session.user
    doc.proposal_number = f"PROP-{random.randint(10000, 99999)}"
    
    # Financials (Manual entry since we removed reqd:1 but we want valid data)
    doc.own_damage_premium = 5000
    doc.third_party_premium = 2000
    doc.addon_premium = 0
    doc.tax_amount = 1260
    # doc.total_premium_payable calculated on save/validate? No, logic is in validate().
    # validate() sums them.
    
    doc.insert(ignore_permissions=True, ignore_mandatory=True)
    
    if status != "Draft":
        # 1. Draft -> Submitted
        from frappe.model.workflow import apply_workflow
        apply_workflow(doc, "Submit")
        doc.reload()
        
        # 2. Submitted -> Underwriting
        from frappe.model.workflow import apply_workflow
        apply_workflow(doc, "Review")
        doc.reload()
        
        # 3. Underwriting -> Approved
        apply_workflow(doc, "Approve")
        doc.reload()
        
        # Sync simple status field if needed (though workflow handles it)
        doc.db_set("status", "Approved")
        
    return doc.name

def create_payment(proposal_name):
    from insurance_erp.insurance_erp.doctype.insurance_proposal.insurance_proposal import create_proposal_payment_entry
    pe_name = create_proposal_payment_entry(proposal_name)
    pe = frappe.get_doc("Payment Entry", pe_name)
    pe.submit()
    
def create_endorsement(policy_name):
    if not frappe.db.exists("Policy Endorsement", {"insurance_policy": policy_name}):
        doc = frappe.new_doc("Policy Endorsement")
        doc.insurance_policy = policy_name
        doc.new_nominee = "Updated Nominee Name"
        doc.insert(ignore_permissions=True, ignore_mandatory=True)
        doc.submit()

def create_claim(policy_name, status):
    doc = frappe.new_doc("Insurance Claim")
    doc.policy = policy_name
    doc.claim_registration_date = today()
    doc.date_of_loss = today()
    doc.nature_of_loss = "Accident"
    doc.claim_amount = 5000
    doc.insert(ignore_permissions=True, ignore_mandatory=True)
    
    if status == "Settled":
        doc.status = "Settled"
        doc.approved_amount = 4000
        doc.deductible_applied = 500
        doc.settlement_amount = 3500
        doc.save()
        doc.submit()

def create_policy_direct(customer, vehicle, plan):
    # Fallback if proposal flow fails (for testing)
    pass

if __name__ == "__main__":
    create_full_dummy_data()
