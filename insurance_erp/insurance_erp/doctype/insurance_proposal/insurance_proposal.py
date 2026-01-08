# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from dateutil.relativedelta import relativedelta


class InsuranceProposal(Document):
	def autoname(self):
		"""Generate proposal number from settings"""
		settings = frappe.get_single("Insurance System Settings")
		self.proposal_number = frappe.model.naming.make_autoname("PROP-.YYYY.-.#####")
	
	def validate(self):
		"""Validate proposal before submission"""
		self.validate_vehicle_customer()
		self.validate_policy_duration()
		self.validate_idv_variance()
	
	def validate_vehicle_customer(self):
		"""Validate customer matches vehicle customer"""
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		if self.customer != vehicle.customer:
			frappe.throw("Proposal customer must match Vehicle customer")
	
	def validate_policy_duration(self):
		"""Validate minimum policy duration"""
		if not self.policy_duration_from or not self.policy_duration_to:
			frappe.throw("Policy duration dates are mandatory")
		
		duration_start = getdate(self.policy_duration_from)
		duration_end = getdate(self.policy_duration_to)
		
		if duration_end < duration_start + relativedelta(months=11):
			frappe.throw("Minimum policy duration is 12 months")
	
	def validate_idv_variance(self):
		"""Validate IDV variance within acceptable range"""
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		if abs(self.vehicle_idv - vehicle.current_idv) / vehicle.current_idv > 0.1:
			frappe.throw("IDV variance exceeds 10% of vehicle current IDV")


@frappe.whitelist()
def create_policy_from_proposal(proposal_name):
	"""Create Insurance Policy from approved proposal"""
	proposal = frappe.get_doc("Insurance Proposal", proposal_name)
	
	# Validate proposal is approved
	if proposal.status != "Approved":
		frappe.throw("Only Approved proposals can be converted to policies")
	
	# Check if policy already exists
	existing_policy = frappe.db.exists("Insurance Policy", {"insurance_proposal": proposal_name})
	if existing_policy:
		frappe.throw(f"Policy already exists for this proposal: {existing_policy}")
	
	# Create new policy
	policy = frappe.new_doc("Insurance Policy")
	policy.customer = proposal.customer
	policy.insurance_proposal = proposal.name
	policy.premium_amount = proposal.premium_amount
	policy.insert(ignore_permissions=True)
	
	frappe.db.commit()
	
	return policy.name
