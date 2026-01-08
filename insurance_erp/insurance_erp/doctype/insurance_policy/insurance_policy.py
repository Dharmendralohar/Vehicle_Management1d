# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class InsurancePolicy(Document):
	def autoname(self):
		"""Generate policy number from settings"""
		settings = frappe.get_single("Insurance System Settings")
		self.policy_number = frappe.model.naming.make_autoname(settings.policy_naming_series)
	
	def before_insert(self):
		"""Copy coverage snapshot from insurance plan"""
		if self.insurance_proposal:
			proposal = frappe.get_doc("Insurance Proposal", self.insurance_proposal)
			plan = frappe.get_doc("Insurance Plan", proposal.insurance_plan)
			
			# Copy dates from proposal
			self.policy_start_date = proposal.policy_duration_from
			self.policy_end_date = proposal.policy_duration_to
			
			# Copy coverage snapshot
			for coverage in plan.coverage_types:
				self.append("coverage_snapshot", {
					"coverage_type": coverage.coverage_type,
					"limit_type": coverage.limit_type,
					"limit_value": coverage.limit_value,
					"deductible": coverage.deductible
				})
	
	def validate(self):
		"""Calculate outstanding amount"""
		self.outstanding_amount = (self.premium_amount or 0) - (self.premium_paid or 0)
		
		# Auto-activate if fully paid
		if self.outstanding_amount == 0 and self.status == "Pending Payment":
			self.status = "Active"
