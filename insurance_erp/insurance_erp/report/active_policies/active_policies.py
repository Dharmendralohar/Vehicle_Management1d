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
			"fieldname": "vehicle",
			"label": "Vehicle",
			"fieldtype": "Link",
			"options": "Vehicle",
			"width": 150
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
			"fieldname": "total_premium_payable",
			"label": "Total Premium",
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
	
	active_filters = {"status": "Active"}
	if filters:
		active_filters.update(filters)

	data = frappe.get_all("Insurance Policy",
		filters=active_filters,
		fields=["name as policy_number", "customer", "vehicle", "policy_start_date", "policy_end_date", "total_premium_payable", "status"],
		order_by="policy_end_date"
	)
	
	return columns, data
