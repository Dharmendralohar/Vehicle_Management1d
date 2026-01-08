# Copyright (c) 2026, Insurance Solutions Inc
# Active Policies Report

import frappe

def execute(filters=None):
	columns = [
		{
			"fieldname": "policy_number",
			"label": "Policy Number",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 180
		},
		{
			"fieldname": "registration_number",
			"label": "Vehicle",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "policy_start_date",
			"label": "Start Date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "policy_end_date",
			"label": "End Date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"fieldname": "grand_total",
			"label": "Premium",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "status",
			"label": "Status",
			"fieldtype": "Data",
			"width": 100
		}
	]
	
	data = frappe.db.sql("""
		SELECT 
			si.policy_number,
			si.customer,
			v.registration_number,
			si.policy_start_date,
			si.policy_end_date,
			si.grand_total,
			si.policy_status
		FROM `tabSales Invoice` si
		LEFT JOIN `tabVehicle` v ON si.vehicle = v.name
		WHERE si.is_insurance_policy = 1
		AND si.policy_status = 'Active'
		ORDER BY si.policy_end_date
	""", as_dict=1)
	
	return columns, data
