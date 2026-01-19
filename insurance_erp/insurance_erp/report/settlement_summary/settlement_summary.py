# Copyright (c) 2026, Insurance Solutions Inc
# Settlement Summary Report

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
			"fieldname": "settlement_amount",
			"label": "Settled Amount",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"fieldname": "settlement_journal_entry",
			"label": "Journal Entry",
			"fieldtype": "Link",
			"options": "Journal Entry",
			"width": 150
		},
		{
			"fieldname": "settlement_date",
			"label": "Settlement Date",
			"fieldtype": "Date",
			"width": 120
		}
	]
	
	data = frappe.db.sql("""
		SELECT 
			c.name as claim_number,
			c.customer,
			c.settlement_amount,
			c.settlement_journal_entry,
			je.posting_date as settlement_date
		FROM `tabInsurance Claim` c
		JOIN `tabJournal Entry` je ON c.settlement_journal_entry = je.name
		WHERE c.claim_status = 'Settled'
		ORDER BY je.posting_date DESC
	""", as_dict=1)
	
	return columns, data
