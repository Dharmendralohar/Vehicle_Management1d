# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class InsuranceProposal(Document):
	def autoname(self):
		"""Generate proposal number from settings"""
		settings = frappe.get_single("Insurance System Settings")
		if settings.policy_naming_series:
			# Using policy series as base for proposal if not separate
			self.name = frappe.model.naming.make_autoname("PROP-.YYYY.-.#####")

	def validate(self):
		"""Validate proposal before submission"""
		self.validate_vehicle()
		self.validate_dates()
		self.validate_idv()

	def validate_vehicle(self):
		if not self.vehicle:
			frappe.throw(_("Vehicle is mandatory"))
		
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		if not vehicle.rc_verified:
			frappe.throw(_("Vehicle RC must be verified before proceeding with the proposal"))
		
		if vehicle.rc_status != "ACTIVE":
			frappe.throw(_("Vehicle RC status must be ACTIVE. Current status: {0}").format(vehicle.rc_status))
		
		if vehicle.rc_expiry_date and getdate(vehicle.rc_expiry_date) < getdate(frappe.utils.today()):
			frappe.throw(_("Vehicle RC has expired. Expiry Date: {0}").format(vehicle.rc_expiry_date))

	def validate_dates(self):
		if not self.policy_duration_from or not self.policy_duration_to:
			frappe.throw(_("Policy Duration From and To are mandatory"))
		
		if getdate(self.policy_duration_to) <= getdate(self.policy_duration_from):
			frappe.throw(_("Policy Duration To must be after Policy Duration From"))

	def validate_idv(self):
		if not self.vehicle_idv or self.vehicle_idv <= 0:
			frappe.throw(_("Vehicle IDV must be a positive value"))

@frappe.whitelist()
def create_policy_from_proposal(proposal_name):
	"""Create Insurance Policy from approved proposal"""
	proposal = frappe.get_doc("Insurance Proposal", proposal_name)
	
	if proposal.workflow_state != "Approved":
		frappe.throw(_("Only Approved proposals can be converted to policies"))
	
	# Check if policy already exists
	existing_policy = frappe.db.exists("Insurance Policy", {"insurance_proposal": proposal_name})
	if existing_policy:
		frappe.throw(_("A policy already exists for this proposal: {0}").format(existing_policy))
	
	policy = frappe.new_doc("Insurance Policy")
	policy.customer = proposal.customer
	policy.insurance_proposal = proposal.name
	policy.insurance_plan = proposal.insurance_plan
	policy.vehicle = proposal.vehicle
	policy.vehicle_idv = proposal.vehicle_idv
	policy.policy_start_date = proposal.policy_duration_from
	policy.policy_end_date = proposal.policy_duration_to
	policy.premium_amount = proposal.premium_amount
	policy.status = "Pending Payment"
	
	policy.insert(ignore_permissions=True)
	frappe.db.commit()
	
	return policy.name
