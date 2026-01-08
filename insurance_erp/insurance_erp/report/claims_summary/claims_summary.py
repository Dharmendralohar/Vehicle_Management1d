# Copyright (c) 2026, Insurance Solutions Inc
# Claims Summary Report

import frappe

def execute(filters=None):
	columns = [
		{
			"fieldname": "claim_number",
			"label": "Claim Number",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 150
		},
		{
			"fieldname": "policy_number",
			"label": "Policy",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "date_of_loss",
			"label": "Date of Loss",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "coverage_type",
			"label": "Coverage",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "claim_amount",
			"label": "Claim Amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "approved_amount",
			"label": "Approved Amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "claim_status",
			"label": "Status",
			"fieldtype": "Data",
			"width": 100
		}
	]
	
	conditions = []
	if filters and filters.get("claim_status"):
		conditions.append(f"claim_status = '{filters.get('claim_status')}'")
	
	where_clause = " AND " + " AND ".join(conditions) if conditions else ""
	
	data = frappe.db.sql(f"""
		SELECT 
			claim_number,
			customer,
			policy_number,
			date_of_loss,
			coverage_type,
			claim_amount,
			approved_amount,
			claim_status
		FROM `tabInsurance Claim`
		WHERE 1=1 {where_clause}
		ORDER BY claim_registration_date DESC
	""", as_dict=1)
	
	return columns, data
