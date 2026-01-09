# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class InsurancePolicy(Document):
	def autoname(self):
		"""Generate policy number from settings"""
		settings = frappe.get_single("Insurance System Settings")
		if settings.policy_naming_series:
			self.name = frappe.model.naming.make_autoname(settings.policy_naming_series)

	def before_insert(self):
		"""Freeze coverage snapshot from insurance plan"""
		if self.insurance_plan:
			plan = frappe.get_doc("Insurance Plan", self.insurance_plan)
			self.set("coverage_snapshot", [])
			for coverage in plan.get("coverage_types", []):
				self.append("coverage_snapshot", {
					"coverage_type": coverage.coverage_type,
					"limit_type": coverage.limit_type,
					"limit_value": coverage.limit_value,
					"deductible": coverage.deductible
				})

	def validate(self):
		"""Update outstanding amount"""
		self.outstanding_amount = (self.premium_amount or 0) - (self.premium_paid or 0)
		self.update_status()

	def update_status(self):
		if self.outstanding_amount <= 0 and self.status == "Pending Payment":
			self.status = "Active"
			# Trigger notification if enabled
			settings = frappe.get_single("Insurance System Settings")
			if settings.notify_customer_on_policy_activation:
				self.notify_activation()

	def notify_activation(self):
		# Placeholder for notification logic (Email Template)
		pass
