# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class InsuranceClaim(Document):
	def autoname(self):
		"""Generate claim number from settings"""
		settings = frappe.get_single("Insurance System Settings")
		if settings.claim_naming_series:
			self.name = frappe.model.naming.make_autoname(settings.claim_naming_series)

	def before_insert(self):
		self.claim_registration_date = frappe.utils.today()
		self.set_details_from_policy()

	def validate(self):
		self.set_details_from_policy()
		self.validate_policy_status()
		self.validate_dates()
		self.validate_coverage()
		self.validate_limits()

	def set_details_from_policy(self):
		if self.policy:
			policy = frappe.get_doc("Sales Invoice", self.policy)
			self.customer = policy.customer
			self.vehicle = policy.vehicle
			self.policy_number = policy.policy_number
			self.insurance_plan = policy.insurance_plan

	def validate_policy_status(self):
		status = frappe.db.get_value("Sales Invoice", self.policy, "policy_status")
		if status != "Active":
			frappe.throw(_("Claims can only be filed against Active policies. Current status: {0}").format(status))

	def validate_dates(self):
		policy = frappe.get_doc("Sales Invoice", self.policy)
		date_of_loss = getdate(self.date_of_loss)
		start_date = getdate(policy.policy_start_date)
		end_date = getdate(policy.policy_end_date)

		if not (start_date <= date_of_loss <= end_date):
			frappe.throw(_("Date of Loss must be within the policy period ({0} to {1})").format(start_date, end_date))

		# Waiting period check
		plan = frappe.get_doc("Insurance Plan", policy.insurance_plan)
		waiting_period = plan.waiting_period_days or 0
		if (date_of_loss - start_date).days < waiting_period:
			frappe.throw(_("Claim filed within waiting period of {0} days.").format(waiting_period))

	def validate_coverage(self):
		policy = frappe.get_doc("Sales Invoice", self.policy)
		has_coverage = False
		for row in policy.get("policy_coverage_snapshot"):
			if row.coverage_type == self.coverage_type:
				has_coverage = True
				break
		
		if not has_coverage:
			frappe.throw(_("Selected coverage type '{0}' is not covered by this policy.").format(self.coverage_type))

	def validate_limits(self):
		settings = frappe.get_single("Insurance System Settings")
		policy = frappe.get_doc("Sales Invoice", self.policy)
		
		# Max claims count
		max_claims = settings.max_claims_per_policy or 999
		existing_claims_count = frappe.db.count("Insurance Claim", {
			"policy": self.policy,
			"name": ["!=", self.name],
			"claim_status": ["not in", ["Rejected"]]
		})
		if existing_claims_count >= max_claims:
			frappe.throw(_("Maximum claims per policy ({0}) reached.").format(max_claims))

		# Max claim amount % of IDV
		max_claim_pct = settings.max_claim_percent_of_idv or 100
		if (self.claim_amount / policy.idv * 100) > max_claim_pct:
			frappe.throw(_("Claim amount exceeds allowed limit ({0}% of IDV). Max allowed: {1}").format(max_claim_pct, (policy.idv * max_claim_pct / 100)))

@frappe.whitelist()
def create_settlement_je(claim_name):
	claim = frappe.get_doc("Insurance Claim", claim_name)
	if claim.claim_status != "Approved":
		frappe.throw(_("Only Approved claims can be settled."))
	
	if claim.settlement_journal_entry:
		frappe.throw(_("Settlement already exists: {0}").format(claim.settlement_journal_entry))

	# Logic to create JE would go here, typically connecting to Finance
	# For now, we simulate or prompt user to create it manually and link it
	frappe.msgprint(_("Please create a Journal Entry and link it to this claim to settle."))
