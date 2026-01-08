# Dummy Data Generation Script for Insurance System
# Run: bench --site test123 execute insurance_erp.create_dummy_data.create_all_dummy_data

import frappe
from frappe.utils import today, add_days, add_months, getdate
from datetime import datetime
import random

def create_all_dummy_data():
	"""Create comprehensive dummy data for insurance system"""
	
	print("\n" + "="*60)
	print("CREATING DUMMY DATA FOR INSURANCE SYSTEM")
	print("="*60 + "\n")
	
	frappe.set_user("Administrator")
	
	# Step 1: Configure Settings
	configure_system_settings()
	
	# Step 2: Create Customers
	customers = create_customers()
	
	# Step 3: Create Vehicles
	vehicles = create_vehicles(customers)
	
	# Step 4: Create Insurance Plans
	plans = create_insurance_plans()
	
	# Step 5: Create Proposals
	proposals = create_proposals(customers, vehicles, plans)
	
	# Step 6: Create Policies
	policies = create_policies(proposals)
	
	# Step 7: Create Claims
	claims = create_claims(policies)
	
	# Step 8: Create Surveys
	surveys = create_surveys(claims)
	
	# Step 9: Create Verifications
	verifications = create_verifications(claims)
	
	frappe.db.commit()
	
	print("\n" + "="*60)
	print("✅ DUMMY DATA CREATION COMPLETED!")
	print("="*60)
	print(f"\nSummary:")
	print(f"  Customers: {len(customers)}")
	print(f"  Vehicles: {len(vehicles)}")
	print(f"  Insurance Plans: {len(plans)}")
	print(f"  Proposals: {len(proposals)}")
	print(f"  Policies: {len(policies)}")
	print(f"  Claims: {len(claims)}")
	print(f"  Surveys: {len(surveys)}")
	print(f"  Verifications: {len(verifications)}")
	print("\nYou can now explore the Insurance System with realistic data!")
	print("="*60 + "\n")


def configure_system_settings():
	"""Configure Insurance System Settings"""
	print("1. Configuring Insurance System Settings...")
	
	settings = frappe.get_single("Insurance System Settings")
	settings.policy_naming_series = "POL-.YYYY.-.#####"
	settings.grace_period_days = 15
	settings.max_claims_per_policy = 3
	settings.max_claim_percent_of_idv = 100
	settings.claim_naming_series = "CLM-.YYYY.-.#####"
	settings.default_claim_waiting_period = 30
	settings.require_survey_before_approval = 1
	settings.require_verification_before_approval = 1
	settings.block_approval_on_fraud_suspected = 1
	settings.notify_customer_on_policy_activation = 1
	settings.notify_customer_on_claim_status_change = 1
	settings.save()
	
	print("   ✓ Settings configured")


def create_customers():
	"""Create dummy customers"""
	print("\n2. Creating Customers...")
	
	customer_data = [
		{"name": "Mr. Rajesh Kumar", "email": "rajesh.kumar@example.com"},
		{"name": "Mrs. Priya Sharma", "email": "priya.sharma@example.com"},
		{"name": "Mr. Amit Patel", "email": "amit.patel@example.com"},
		{"name": "Ms. Sneha Rao", "email": "sneha.rao@example.com"},
		{"name": "Mr. Vikram Singh", "email": "vikram.singh@example.com"}
	]
	
	customers = []
	for data in customer_data:
		if not frappe.db.exists("Customer", data["name"]):
			customer = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": data["name"],
				"customer_type": "Individual",
				"customer_group": "Individual",
				"territory": "India"
			})
			customer.insert(ignore_permissions=True)
			customers.append(customer.name)
			print(f"   ✓ Created customer: {customer.name}")
		else:
			customers.append(data["name"])
			print(f"   ✓ Customer exists: {data['name']}")
	
	return customers


def create_vehicles(customers):
	"""Create dummy vehicles"""
	print("\n3. Creating Vehicles...")
	
	vehicle_data = [
		{"customer": customers[0], "reg": "MH01AB1234", "make": "Honda", "model": "City", "year": 2023, "idv": 800000},
		{"customer": customers[1], "reg": "DL05CD5678", "make": "Maruti", "model": "Swift", "year": 2022, "idv": 650000},
		{"customer": customers[2], "reg": "KA03EF9012", "make": "Hyundai", "model": "Creta", "year": 2024, "idv": 1200000},
		{"customer": customers[3], "reg": "TN09GH3456", "make": "Tata", "model": "Nexon", "year": 2023, "idv": 950000},
		{"customer": customers[4], "reg": "GJ01IJ7890", "make": "Mahindra", "model": "XUV700", "year": 2024, "idv": 1500000}
	]
	
	vehicles = []
	for idx, data in enumerate(vehicle_data):
		if not frappe.db.exists("Vehicle", {"registration_number": data["reg"]}):
			vehicle = frappe.get_doc({
				"doctype": "Vehicle",
				"customer": data["customer"],
				"registration_number": data["reg"],
				"chassis_number": f"CHASSIS{random.randint(100000, 999999)}",
				"engine_number": f"ENG{random.randint(100000, 999999)}",
				"make": data["make"],
				"model": data["model"],
				"manufacturing_year": data["year"],
				"fuel_type": "Petrol",
				"vehicle_type": "Four Wheeler",
				"current_idv": data["idv"]
			})
			vehicle.flags.ignore_validate = True
			vehicle.flags.ignore_mandatory = True
			vehicle.insert(ignore_permissions=True, ignore_if_duplicate=True)
			vehicles.append(vehicle.name)
			print(f"   ✓ Created vehicle: {data['reg']}")
		else:
			vehicles.append(frappe.db.get_value("Vehicle", {"registration_number": data["reg"]}, "name"))
			print(f"   ✓ Vehicle exists: {data['reg']}")
	
	return vehicles


def create_insurance_plans():
	"""Create dummy insurance plans"""
	print("\n4. Creating Insurance Plans...")
	
	plan_data = [
		{
			"name": "Comprehensive Plan 2026",
			"code": "COMP-2026",
			"type": "Comprehensive",
			"premium": 15000,
			"coverages": [
				{"type": "Own Damage (OD)", "limit_type": "Percentage of IDV", "value": 100, "deductible": 2000},
				{"type": "Third Party (TP)", "limit_type": "Fixed Amount", "value": 75000, "deductible": 0},
				{"type": "Fire", "limit_type": "Percentage of IDV", "value": 80, "deductible": 1000},
				{"type": "Theft", "limit_type": "Percentage of IDV", "value": 100, "deductible": 2000}
			]
		},
		{
			"name": "Third Party Only 2026",
			"code": "TP-2026",
			"type": "Third Party",
			"premium": 5000,
			"coverages": [
				{"type": "Third Party (TP)", "limit_type": "Fixed Amount", "value": 75000, "deductible": 0}
			]
		},
		{
			"name": "Premium Comprehensive 2026",
			"code": "PREM-2026",
			"type": "Comprehensive",
			"premium": 25000,
			"coverages": [
				{"type": "Own Damage (OD)", "limit_type": "Percentage of IDV", "value": 100, "deductible": 0},
				{"type": "Third Party (TP)", "limit_type": "Fixed Amount", "value": 100000, "deductible": 0},
				{"type": "Fire", "limit_type": "Percentage of IDV", "value": 100, "deductible": 0},
				{"type": "Theft", "limit_type": "Percentage of IDV", "value": 100, "deductible": 0},
				{"type": "Flood", "limit_type": "Percentage of IDV", "value": 80, "deductible": 0},
				{"type": "Zero Depreciation", "limit_type": "Percentage of IDV", "value": 100, "deductible": 0}
			]
		}
	]
	
	plans = []
	for data in plan_data:
		if not frappe.db.exists("Insurance Plan", data["name"]):
			plan = frappe.get_doc({
				"doctype": "Insurance Plan",
				"plan_name": data["name"],
				"plan_code": data["code"],
				"policy_type": data["type"],
				"is_active": 1,
				"base_premium": data["premium"],
				"max_claim_percent_of_idv": 100,
				"deductible_amount": 2000,
				"waiting_period_days": 0
			})
			
			for cov in data["coverages"]:
				plan.append("coverage_types", {
					"coverage_type": cov["type"],
					"limit_type": cov["limit_type"],
					"limit_value": cov["value"],
					"deductible": cov["deductible"]
				})
			
			plan.insert(ignore_permissions=True)
			plans.append(plan.name)
			print(f"   ✓ Created plan: {data['name']}")
		else:
			plans.append(data["name"])
			print(f"   ✓ Plan exists: {data['name']}")
	
	return plans


def create_proposals(customers, vehicles, plans):
	"""Create dummy proposals"""
	print("\n5. Creating Insurance Proposals...")
	
	proposals = []
	for i in range(min(len(vehicles), 5)):
		# Get vehicle to match customer
		vehicle = frappe.get_doc("Vehicle", vehicles[i])
		
		proposal = frappe.get_doc({
			"doctype": "Insurance Proposal",
			"customer": vehicle.customer,  # Use vehicle's customer
			"proposal_date": add_days(today(), -60),
			"status": "Approved" if i < 3 else "Draft",
			"vehicle": vehicles[i],
			"insurance_plan": plans[i % len(plans)],
			"premium_amount": [15000, 5000, 25000, 15000, 25000][i],
			"policy_duration_from": today(),
			"policy_duration_to": add_months(today(), 12),
			"risk_assessment_notes": "Good driving history, no prior claims"
		})
		proposal.flags.ignore_validate = False  # Let it validate properly
		proposal.insert(ignore_permissions=True)
		
		if proposal.status == "Approved":
			proposal.submit()
		
		proposals.append(proposal.name)
		print(f"   ✓ Created proposal: {proposal.proposal_number} ({proposal.status})")
	
	return proposals


def create_policies(proposals):
	"""Create dummy policies"""
	print("\n6. Creating Insurance Policies...")
	
	policies = []
	# Only create policies for approved proposals (first 3)
	for i in range(3):
		proposal = frappe.get_doc("Insurance Proposal", proposals[i])
		
		policy = frappe.get_doc({
			"doctype": "Insurance Policy",
			"customer": proposal.customer,
			"policy_date": today(),
			"status": "Active" if i < 2 else "Pending Payment",
			"insurance_proposal": proposal.name
		})
		policy.insert(ignore_permissions=True)
		
		# Mark first 2 policies as paid
		if i < 2:
			policy.premium_paid = policy.premium_amount
			policy.save(ignore_permissions=True)
		
		policy.submit()
		policies.append(policy.name)
		print(f"   ✓ Created policy: {policy.policy_number} ({policy.status})")
	
	return policies


def create_claims(policies):
	"""Create dummy claims"""
	print("\n7. Creating Insurance Claims...")
	
	claims = []
	# Create claims only for active policies (first 2)
	for i in range(2):
		policy = frappe.get_doc("Insurance Policy", policies[i])
		
		# Use policy start date + 60 days for date of loss
		date_of_loss = add_days(policy.policy_start_date, 60)
		claim_reg_date = add_days(date_of_loss, 2)
		
		# Get first available coverage type from policy
		coverage_type = policy.coverage_snapshot[0].coverage_type if policy.coverage_snapshot else "Own Damage (OD)"
		
		claim = frappe.get_doc({
			"doctype": "Insurance Claim",
			"customer": policy.customer,
			"policy": policy.name,
			"date_of_loss": date_of_loss,
			"claim_registration_date": claim_reg_date,
			"coverage_type": coverage_type,
			"incident_description": f"Front bumper damage due to collision at traffic signal",
			"claim_amount": [50000, 75000][i],
			"claim_status": "Survey Completed" if i == 0 else "Reported"
		})
		claim.insert(ignore_permissions=True)
		claim.submit()
		claims.append(claim.name)
		print(f"   ✓ Created claim: {claim.claim_number} ({claim.claim_status})")
	
	return claims


def create_surveys(claims):
	"""Create dummy surveys"""
	print("\n8. Creating Claim Surveys...")
	
	surveys = []
	# Create survey only for first claim
	if len(claims) > 0:
		claim = frappe.get_doc("Insurance Claim", claims[0])
		survey_date = add_days(claim.claim_registration_date, 3)
		
		survey = frappe.get_doc({
			"doctype": "Claim Survey",
			"claim": claim.name,
			"surveyor": "Administrator",
			"survey_date": survey_date,
			"damage_description": "Front bumper dented, right headlight broken, minor scratches on hood",
			"estimated_repair_cost": 48000,
			"is_total_loss": 0
		})
		survey.insert(ignore_permissions=True)
		survey.submit()
		surveys.append(survey.name)
		print(f"   ✓ Created survey for claim: {claim.claim_number}")
	
	return surveys


def create_verifications(claims):
	"""Create dummy verifications"""
	print("\n9. Creating Claim Verifications...")
	
	verifications = []
	# Create verification only for first claim
	if len(claims) > 0:
		claim = frappe.get_doc("Insurance Claim", claims[0])
		verification_date = add_days(claim.claim_registration_date, 5)
		
		verification = frappe.get_doc({
			"doctype": "Claim Verification",
			"claim": claim.name,
			"verification_agent": "Administrator",
			"verification_date": verification_date,
			"field_visit_completed": 1,
			"field_visit_notes": "Verified accident location and damage. Damage consistent with incident report.",
			"fraud_suspected": 0,
			"recommendation": "Approve"
		})
		verification.insert(ignore_permissions=True)
		verification.submit()
		verifications.append(verification.name)
		print(f"   ✓ Created verification for claim: {claim.claim_number}")
	
	return verifications


if __name__ == "__main__":
	create_all_dummy_data()
