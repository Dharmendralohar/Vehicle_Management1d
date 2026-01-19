# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class InsurancePolicy(Document):
	def before_insert(self):
		"""Capture snapshots before the policy is created"""
		self.freeze_snapshots()

	def validate(self):
		self.validate_mandatory_policy_data()
		self.calculate_outstanding()
		self.update_status()

	def freeze_snapshots(self):
		"""Freeze the Insurance Plan and its coverages at the time of policy creation"""
		if not self.insurance_plan:
			return

		plan = frappe.get_doc("Insurance Plan", self.insurance_plan)
		
		# Freeze Plan JSON
		self.plan_snapshot_json = frappe.as_json(plan.as_dict())
		
		# Freeze Coverage Snapshot Table
		self.set("coverage_snapshot", [])
		for coverage in plan.get("coverage_types", []):
			self.append("coverage_snapshot", {
				"coverage_type": coverage.coverage_type,
				"limit_type": coverage.limit_type,
				"limit_value": coverage.limit_value,
				"deductible": coverage.deductible
			})

	def validate_mandatory_policy_data(self):
		"""Ensure critical policy fields are populated"""
		mandatory = ["customer", "vehicle", "insurance_plan", "total_premium_payable"]
		for field in mandatory:
			if not self.get(field):
				frappe.throw(_("Field {0} is mandatory for Policy").format(self.meta.get_label(field)))

	def calculate_outstanding(self):
		"""Recalculate outstanding amount based on paid amount"""
		self.outstanding_amount = flt(self.total_premium_payable) - flt(self.premium_paid)

	def update_status(self):
		"""Update status to Active if fully paid"""
		if flt(self.outstanding_amount) <= 0 and self.status == "Pending Payment":
			self.status = "Active"
