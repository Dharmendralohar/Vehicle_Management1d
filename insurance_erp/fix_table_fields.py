# Fix missing table fields

import frappe

def fix_table_fields():
	"""Manually create the two table fields that failed"""
	
	# 1. Coverage Types table for Item
	if not frappe.db.exists("Custom Field", {"dt": "Item", "fieldname": "coverage_types"}):
		frappe.get_doc({
			"doctype": "Custom Field",
			"dt": "Item",
			"fieldname": "coverage_types",
			"fieldtype": "Table",
			"label": "Coverage Types",
			"insert_after": "coverage_types_section",
			"options": "Insurance Coverage Type",
			"depends_on": "eval:doc.is_insurance_plan==1"
		}).insert(ignore_permissions=True)
		print("✓ Created coverage_types field for Item")
	else:
		print("✓ coverage_types field already exists for Item")
	
	# 2. Coverage Snapshot table for Sales Invoice
	if not frappe.db.exists("Custom Field", {"dt": "Sales Invoice", "fieldname": "coverage_snapshot"}):
		frappe.get_doc({
			"doctype": "Custom Field",
			"dt": "Sales Invoice",
			"fieldname": "coverage_snapshot",
			"fieldtype": "Table",
			"label": "Coverage Snapshot",
			"insert_after": "coverage_snapshot_section",
			"options": "Policy Coverage Snapshot",
			"depends_on": "eval:doc.is_insurance_policy==1",
			"read_only": 1
		}).insert(ignore_permissions=True)
		print("✓ Created coverage_snapshot field for Sales Invoice")
	else:
		print("✓ coverage_snapshot field already exists for Sales Invoice")
	
	frappe.db.commit()
	frappe.clear_cache()
	print("\n✅ All custom fields imported successfully!")

if __name__ == "__main__":
	fix_table_fields()
