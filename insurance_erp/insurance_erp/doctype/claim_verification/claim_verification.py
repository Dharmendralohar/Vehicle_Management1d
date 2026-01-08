# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ClaimVerification(Document):
	def on_submit(self):
		"""Update claim status and fraud flag when verification is submitted"""
		claim = frappe.get_doc("Insurance Claim", self.claim)
		claim.db_set("claim_status", "Agent Verified", notify=True, commit=True)
		claim.db_set("verification", self.name, notify=True, commit=True)
		
		if self.fraud_suspected:
			claim.db_set("fraud_suspected", 1, notify=True, commit=True)
		
		frappe.msgprint(f"Claim {claim.claim_number} status updated to Agent Verified")
