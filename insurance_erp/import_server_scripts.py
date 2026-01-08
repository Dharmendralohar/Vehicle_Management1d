# Server Scripts Import Script
# This will create all server scripts in the system

import frappe
import json
import os

def import_server_scripts():
	"""Import all server scripts for insurance automation"""
	
	fixtures_path = frappe.get_app_path("insurance_erp", "server_scripts")
	
	if not os.path.exists(fixtures_path):
		print(f"Server scripts directory not found: {fixtures_path}")
		return
	
	server_scripts = [
		{
			"file": "sales_order_proposal_validation.json",
			"description": "Sales Order - Proposal Validation"
		},
		{
			"file": "sales_invoice_policy_creation.json",
			"description": "Sales Invoice - Policy Creation"
		},
		{
			"file": "payment_entry_policy_activation.json",
			"description": "Payment Entry - Policy Activation"
		},
		{
			"file": "journal_entry_settlement_update.json",
			"description": "Journal Entry - Settlement Update"
		}
	]
	
	for script_info in server_scripts:
		file_path = os.path.join(fixtures_path, script_info["file"])
		
		if not os.path.exists(file_path):
			print(f"  ✗ File not found: {file_path}")
			continue
		
		print(f"\nImporting {script_info['description']}...")
		
		with open(file_path, 'r') as f:
			script_data = json.load(f)
		
		# Check if server script already exists
		existing = frappe.db.exists("Server Script", script_data["name"])
		
		if existing:
			# Update existing
			doc = frappe.get_doc("Server Script", script_data["name"])
			doc.update(script_data)
			doc.save(ignore_permissions=True)
			print(f"  ✓ Updated: {script_data['name']}")
		else:
			# Create new
			doc = frappe.get_doc({
				"doctype": "Server Script",
				**script_data
			})
			doc.insert(ignore_permissions=True)
			print(f"  ✓ Created: {script_data['name']}")
	
	frappe.db.commit()
	frappe.clear_cache()
	
	print("\n✅ All server scripts imported successfully!")
	print("\nServer Scripts Created:")
	print("1. Sales Order - Validates insurance proposals before submission")
	print("2. Sales Invoice - Auto-creates policy from approved proposal")
	print("3. Payment Entry - Activates policy when fully paid")
	print("4. Journal Entry - Updates claim status to Settled")

if __name__ == "__main__":
	import_server_scripts()
