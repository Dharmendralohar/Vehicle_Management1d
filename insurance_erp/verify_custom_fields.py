# Verify Custom Fields Import

import frappe

def verify_custom_fields():
	"""Verify all custom fields were imported correctly"""
	
	doctypes_to_check = {
		"Item": [
			"insurance_plan_section",
			"is_insurance_plan",
			"policy_type",
			"max_claim_percent_of_idv",
			"deductible_amount",
			"waiting_period_days",
			"coverage_types_section",
			"coverage_types"
		],
		"Sales Order": [
			"insurance_proposal_section",
			"is_insurance_proposal",
			"vehicle",
			"vehicle_idv",
			"policy_duration_from",
			"policy_duration_to",
			"risk_assessment_section",
			"risk_assessment_notes",
			"underwriter_remarks"
		],
		"Sales Invoice": [
			"insurance_policy_section",
			"is_insurance_policy",
			"policy_number",
			"policy_status",
			"policy_start_date",
			"policy_end_date",
			"vehicle_details_section",
			"vehicle",
			"vehicle_idv",
			"source_proposal",
			"coverage_snapshot_section",
			"coverage_snapshot"
		]
	}
	
	print("\n" + "="*60)
	print("CUSTOM FIELDS VERIFICATION REPORT")
	print("="*60 + "\n")
	
	total_fields = 0
	total_found = 0
	
	for doctype, fields in doctypes_to_check.items():
		print(f"\n{doctype}:")
		print("-" * 40)
		
		for fieldname in fields:
			exists = frappe.db.exists("Custom Field", {
				"dt": doctype,
				"fieldname": fieldname
			})
			
			total_fields += 1
			if exists:
				total_found += 1
				print(f"  ✓ {fieldname}")
			else:
				print(f"  ✗ {fieldname} - MISSING!")
	
	print("\n" + "="*60)
	print(f"SUMMARY: {total_found}/{total_fields} custom fields imported")
	print("="*60 + "\n")
	
	if total_found == total_fields:
		print("✅ All custom fields imported successfully!")
		print("\nNext steps:")
		print("1. Reload your desk (Ctrl+R)")
		print("2. Go to Item List and create a new Insurance Plan")
		print("3. Go to Sales Order and create a new Proposal")
		print("4. Go to Sales Invoice and verify policy fields appear")
	else:
		print("⚠️ Some custom fields are missing. Please check the errors above.")

if __name__ == "__main__":
	verify_custom_fields()
