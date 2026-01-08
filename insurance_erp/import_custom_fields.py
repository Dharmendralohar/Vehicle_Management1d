# Copyright (c) 2026, Insurance Solutions Inc
# Programmatic Custom Fields Import Script

import frappe
import json
import os

def import_custom_fields():
	"""Import all custom fields for ERPNext standard DocTypes"""
	
	fixtures_path = frappe.get_app_path("insurance_erp", "fixtures")
	
	# Define custom field files
	custom_field_files = [
		{
			"file": "custom_fields_item.json",
			"doctype": "Item",
			"description": "Insurance Plan fields"
		},
		{
			"file": "custom_fields_sales_order.json",
			"doctype": "Sales Order",
			"description": "Insurance Proposal fields"
		},
		{
			"file": "custom_fields_sales_invoice.json",
			"doctype": "Sales Invoice",
			"description": "Insurance Policy fields"
		}
	]
	
	for cf_file in custom_field_files:
		file_path = os.path.join(fixtures_path, cf_file["file"])
		
		if not os.path.exists(file_path):
			frappe.throw(f"File not found: {file_path}")
		
		print(f"\nImporting {cf_file['description']} for {cf_file['doctype']}...")
		
		with open(file_path, 'r') as f:
			fields = json.load(f)
		
		for field in fields:
			field['dt'] = cf_file['doctype']
			
			# Check if custom field already exists
			existing = frappe.db.exists("Custom Field", {
				"dt": cf_file['doctype'],
				"fieldname": field['fieldname']
			})
			
			if existing:
				print(f"  ✓ Field '{field['fieldname']}' already exists, skipping...")
				continue
			
			try:
				cf = frappe.get_doc({
					'doctype': 'Custom Field',
					**field
				})
				cf.insert(ignore_permissions=True)
				print(f"  ✓ Created field: {field['fieldname']}")
			except Exception as e:
				print(f"  ✗ Error creating field {field['fieldname']}: {str(e)}")
	
	frappe.db.commit()
	frappe.clear_cache()
	
	print("\n✅ Custom fields import completed!")
	print("Please reload your desk to see the changes.")

if __name__ == "__main__":
	import_custom_fields()
