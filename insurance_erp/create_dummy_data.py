import frappe
from frappe.utils import add_days, today

def create_system_settings():
    if not frappe.db.exists("Insurance System Settings", "Insurance System Settings"):
        settings = frappe.get_single("Insurance System Settings")
        settings.update({
            "policy_naming_series": "POL-.YYYY.-",
            "grace_period": 30,
            "max_claims_per_policy": 3,
            "max_claim_percent_of_idv": 100,
            "limits_of_liability": "As per Motor Vehicle Act 1988",
            "usage_restrictions": "Personal Use Only",
            "driver_clauses": "Any person including the insured provided that a person driving holds an effective driving license.",
            "insurance_act_declaration": "I/We hereby declare that the statements made by me/us in this Proposal Form are true to the best of my/our knowledge.",
            "motor_vehicle_act_reference": "Section 146 of the Motor Vehicles Act, 1988"
        })
        settings.save()
        print("Insurance System Settings created.")

def create_insurance_plan():
    if not frappe.db.exists("Insurance Plan", "Gold Comprehensive Plan"):
        plan = frappe.new_doc("Insurance Plan")
        plan.plan_name = "Gold Comprehensive Plan"
        plan.plan_code = "GCP-001"
        plan.insurance_type = "Package Policy"
        plan.base_premium = 5000
        plan.idv_calculation_rule = "Depreciation Based"
        plan.deductible_amount = 1000
        plan.tp_liability_limit = 750000
        plan.pa_owner_driver_limit = 1500000
        plan.passenger_cover_limit = 200000
        
        # Slabs
        plan.append("depreciation_slabs", {
            "from_age_months": 0,
            "to_age_months": 6,
            "depreciation_percent": 5
        })
        plan.append("depreciation_slabs", {
            "from_age_months": 6,
            "to_age_months": 12,
            "depreciation_percent": 10
        })
        
        # Coverage
        plan.append("coverage_types", {
            "coverage_type": "Accident",
            "limit_type": "Percentage of IDV",
            "limit_value": 100,
            "deductible": 1000
        })
        plan.append("coverage_types", {
            "coverage_type": "Fire",
            "limit_type": "Percentage of IDV",
            "limit_value": 100,
            "deductible": 0
        })
        
        plan.insert()
        print("Insurance Plan 'Gold Comprehensive Plan' created.")

def create_customer_and_address():
    if not frappe.db.exists("Customer", "John Insurance"):
        customer = frappe.new_doc("Customer")
        customer.customer_name = "John Insurance"
        customer.customer_type = "Individual"
        customer.customer_group = "All Customer Groups"
        customer.territory = "All Territories"
        customer.mobile_no = "+919999999999"
        customer.email_id = "john@example.com"
        customer.insert()
        print("Customer 'John Insurance' created.")

    if not frappe.db.exists("Address", "John-Address"):
        address = frappe.new_doc("Address")
        address.address_title = "John Insurance"
        address.address_line1 = "123 Insurance Street"
        address.city = "Mumbai"
        address.state = "Maharashtra"
        address.pincode = "400001"
        address.country = "India"
        address.append("links", {
            "link_doctype": "Customer",
            "link_name": "John Insurance"
        })
        address.insert()
        print("Address for 'John Insurance' created.")

def create_vehicle():
    if not frappe.db.exists("Vehicle", "MH-01-AB-1234"):
        vehicle = frappe.new_doc("Vehicle")
        vehicle.license_plate = "MH-01-AB-1234"
        vehicle.make = "Tesla"
        vehicle.model = "Model 3"
        vehicle.fuel_type = "Electric"
        vehicle.chassis_no = "TSL3CHASSIS998877"
        vehicle.vehicle_value = 4000000
        vehicle.last_odometer = 500
        
        # Check for UOM
        if not frappe.db.exists("UOM", "Km"):
            frappe.get_doc({"doctype": "UOM", "uom_name": "Km"}).insert(ignore_permissions=True)
        vehicle.uom = "Km"
        
        # Custom Fields
        vehicle.custom_rto_location = "Mumbai South"
        vehicle.custom_vehicle_category = "Private Car"
        vehicle.custom_body_type = "Sedan"
        vehicle.custom_engine_cc = 1200
        vehicle.custom_manufacturing_year = 2024
        vehicle.custom_seating_capacity = 5
        vehicle.custom_engine_number = "EMOTOR776655"
        vehicle.custom_vehicle_idv = 3800000
        
        vehicle.insert()
        print("Vehicle 'MH-01-AB-1234' created.")

def create_proposal():
    if not frappe.db.exists("Insurance Proposal", "PROP-2024-001"):
        proposal = frappe.new_doc("Insurance Proposal")
        proposal.proposal_number = "PROP-2024-001"
        proposal.customer = "John Insurance"
        proposal.vehicle = "MH-01-AB-1234"
        proposal.agent = "Administrator"
        proposal.no_claim_bonus_percent = 20
        proposal.insurance_plan = "Gold Comprehensive Plan"
        proposal.policy_duration_from = today()
        proposal.policy_duration_to = add_days(today(), 365)
        proposal.own_damage_premium = 12000
        proposal.third_party_premium = 3500
        proposal.addon_premium = 2000
        proposal.tax_amount = 2790
        proposal.total_premium_payable = 20290
        
        # Calculated fields will be handled by validate() if implemented correctly
        proposal.insert()
        print("Insurance Proposal for John Insurance created.")

def main():
    try:
        # Cleanup existing dummy records to ensure fresh state
        frappe.db.delete("Insurance Proposal", {"proposal_number": "PROP-2024-001"})
        frappe.db.delete("Vehicle", {"license_plate": "MH-01-AB-1234"})
        frappe.db.delete("Address", {"address_title": "John Insurance"})
        frappe.db.delete("Customer", {"customer_name": "John Insurance"})
        frappe.db.delete("Insurance Plan", {"plan_name": "Gold Comprehensive Plan"})
        
        create_system_settings()
        create_insurance_plan()
        create_customer_and_address()
        create_vehicle()
        create_proposal()
        frappe.db.commit()
        print("Dummy data population complete.")
    except Exception as e:
        frappe.db.rollback()
        print(f"Error creating dummy data: {e}")
        raise e

if __name__ == "__main__":
    main()
