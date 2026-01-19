# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, flt
import json

class InsuranceClaim(Document):
	def validate(self):
		"""Validate claim details before submission"""
		self.validate_mandatory_claim_data()
		self.validate_policy_status()
		self.validate_dates()
		self.validate_coverage()
		self.validate_limits()
		
		if self.docstatus == 1:
			self.validate_settlement_data()

	def validate_settlement_data(self):
		"""Point 7: Enforce full settlement data before approval/submission"""
		mandatory = ["approved_amount", "settlement_amount", "deductible_applied"]
		for field in mandatory:
			if not self.get(field):
				frappe.throw(_("Field {0} is mandatory for Claim Settlement/Submission").format(self.meta.get_label(field)))

	def validate_mandatory_claim_data(self):
		"""Ensure all Indian standard claim fields are populated"""
		mandatory = ["policy", "claim_registration_date", "date_of_loss", "nature_of_loss", "claim_amount"]
		for field in mandatory:
			if not self.get(field):
				frappe.throw(_("Field {0} is mandatory for Claim").format(self.meta.get_label(field)))

	def validate_policy_status(self):
		"""Ensure claim is only filed against an Active policy"""
		policy = frappe.get_doc("Insurance Policy", self.policy)
		if policy.status != "Active":
			frappe.throw(_("Claims can only be filed against Active policies. Current policy status: {0}").format(policy.status))

	def validate_dates(self):
		"""Ensure claim dates are valid w.r.t policy period"""
		policy = frappe.get_doc("Insurance Policy", self.policy)
		
		# Loss date within policy period
		if getdate(self.date_of_loss) < getdate(policy.policy_start_date) or \
		   getdate(self.date_of_loss) > getdate(policy.policy_end_date):
			frappe.throw(_("Date of Loss ({0}) must be within Policy Period ({1} to {2})").format(
				self.date_of_loss, policy.policy_start_date, policy.policy_end_date
			))
		
		# Loss date before claim date
		if getdate(self.date_of_loss) > getdate(self.claim_registration_date):
			frappe.throw(_("Loss Date cannot be after Claim Date"))

	def validate_coverage(self):
		"""Verify that the nature of loss is covered by the policy snapshot"""
		policy = frappe.get_doc("Insurance Policy", self.policy)
		
		# Check coverage_snapshot table on policy
		found = False
		for row in policy.get("coverage_snapshot", []):
			if row.coverage_type == self.nature_of_loss:
				found = True
				break
		
		if not found:
			frappe.msgprint(_("Warning: Nature of Loss '{0}' might not be explicitly listed in policy coverage snapshot.").format(self.nature_of_loss))

	def validate_limits(self):
		"""Ensure claimed amount doesn't exceed IDV or specific plan limits"""
		policy = frappe.get_doc("Insurance Policy", self.policy)
		
		if flt(self.claim_amount) > flt(policy.vehicle_idv):
			frappe.throw(_("Claimed amount ({0}) exceeds the Insured Declared Value (IDV) of {1}").format(
				self.claim_amount, policy.vehicle_idv
			))
