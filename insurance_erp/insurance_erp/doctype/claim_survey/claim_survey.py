# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClaimSurvey(Document):
	def on_submit(self):
		"""Update claim status when survey is submitted"""
		claim = frappe.get_doc("Insurance Claim", self.claim)
		claim.db_set("claim_status", "Survey Completed", notify=True, commit=True)
		claim.db_set("survey", self.name, notify=True, commit=True)
		
		frappe.msgprint(f"Claim {claim.claim_number} status updated to Survey Completed")
