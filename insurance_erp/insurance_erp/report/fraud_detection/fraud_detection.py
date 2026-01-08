# Copyright (c) 2026, Insurance Solutions Inc
# Fraud Detection Report

import frappe

def execute(filters=None):
	columns = [
		{
			"fieldname": "claim_number",
			"label": "Claim Number",
			"fieldtype": "Link",
			"options": "Insurance Claim",
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
			"fieldname": "claim_amount",
			"label": "Claim Amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "claim_status",
			"label": "Status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "verification",
			"label": "Verification",
			"fieldtype": "Link",
			"options": "Claim Verification",
			"width": 150
		}
	]
	
	data = frappe.db.sql("""
		SELECT 
			claim_number,
			customer,
			policy_number,
			claim_amount,
			claim_status,
			verification
		FROM `tabInsurance Claim`
		WHERE fraud_suspected = 1
		ORDER BY claim_registration_date DESC
	""", as_dict=1)
	
	return columns, data
