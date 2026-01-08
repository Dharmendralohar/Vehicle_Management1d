# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, add_days


class InsuranceClaim(Document):
	def autoname(self):
		"""Generate claim number from settings"""
		settings = frappe.get_single("Insurance System Settings")
		self.claim_number = frappe.model.naming.make_autoname(settings.claim_naming_series)
	
	def validate(self):
		"""Validate claim before submission"""
		self.validate_status()
		self.validate_date_of_loss()
		self.validate_waiting_period()
		self.validate_coverage_exists()
		self.validate_claim_amount_limits()
		self.validate_max_claims_per_policy()
	
	def validate_status(self):
		"""Validate policy is active"""
		policy = frappe.get_doc("Insurance Policy", self.policy)
		
		if policy.status != "Active":
			frappe.throw(f"Policy {policy.policy_number} is not Active. Current status: {policy.status}")
	
	def validate_date_of_loss(self):
		"""Validate date of loss is within policy period"""
		policy = frappe.get_doc("Insurance Policy", self.policy)
		
		date_of_loss = getdate(self.date_of_loss)
		policy_start = getdate(policy.policy_start_date)
		policy_end = getdate(policy.policy_end_date)
		
		if not (policy_start <= date_of_loss <= policy_end):
			frappe.throw(f"Date of loss must be between {policy_start} and {policy_end}")
	
	def validate_waiting_period(self):
		"""Validate waiting period has elapsed"""
		settings = frappe.get_single("Insurance System Settings")
		policy = frappe.get_doc("Insurance Policy", self.policy)
		
		policy_start = getdate(policy.policy_start_date)
		date_of_loss = getdate(self.date_of_loss)
		days_since_policy_start = (date_of_loss - policy_start).days
		
		if days_since_policy_start < settings.default_claim_waiting_period:
			frappe.throw(
				f"Claim cannot be filed within waiting period of {settings.default_claim_waiting_period} days. "
				f"Policy started on {policy_start}, only {days_since_policy_start} days have elapsed"
			)
	
	def validate_coverage_exists(self):
		"""Validate coverage type exists in policy"""
		policy = frappe.get_doc("Insurance Policy", self.policy)
		
		coverage_exists = any(
			cov.coverage_type == self.coverage_type
			for cov in policy.coverage_snapshot
		)
		
		if not coverage_exists:
			frappe.throw(f"Coverage type '{self.coverage_type}' not found in policy")
	
	def validate_claim_amount_limits(self):
		"""Validate total claims don't exceed IDV percentage"""
		settings = frappe.get_single("Insurance System Settings")
		policy = frappe.get_doc("Insurance Policy", self.policy)
		vehicle_idv = policy.vehicle_idv
		
		# Get existing claims
		existing_claims = frappe.get_all("Insurance Claim",
			filters={
				"policy": self.policy,
				"status": ["!=", "Rejected"],
				"name": ["!=", self.name]
			},
			fields=["claim_amount"]
		)
		
		total_claimed = sum([c.claim_amount for c in existing_claims]) + self.claim_amount
		
		if (total_claimed / vehicle_idv * 100) > settings.max_claim_percent_of_idv:
			frappe.throw(f"Total claims exceed {settings.max_claim_percent_of_idv}% of IDV")
	
	def validate_max_claims_per_policy(self):
		"""Validate max claims per policy not exceeded"""
		settings = frappe.get_single("Insurance System Settings")
		
		existing_claims_count = frappe.db.count("Insurance Claim",
			filters={
				"policy": self.policy,
				"status": ["!=", "Rejected"],
				"name": ["!=", self.name]
			}
		)
		
		if existing_claims_count >= settings.max_claims_per_policy:
			frappe.throw(f"Maximum {settings.max_claims_per_policy} claims per policy exceeded")


@frappe.whitelist()
def create_settlement_journal_entry(claim_name):
	"""Create settlement Journal Entry for approved claim"""
	claim = frappe.get_doc("Insurance Claim", claim_name)
	
	if claim.status != "Approved":
		frappe.throw("Claim must be Approved to create settlement")
	
	if claim.settlement_journal_entry:
		frappe.throw(f"Settlement already created: {claim.settlement_journal_entry}")
	
	# Create Journal Entry
	je = frappe.new_doc("Journal Entry")
	je.voucher_type = "Journal Entry"
	je.posting_date = frappe.utils.today()
	je.user_remark = f"Claim Settlement for {claim.claim_number}"
	je.company = frappe.defaults.get_user_default("Company")
	
	# Debit: Claims Expense Account
	je.append("accounts", {
		"account": f"Claims Expense - {je.company}",  # Adjust account name as needed
		"debit_in_account_currency": claim.approved_amount or claim.claim_amount
	})
	
	# Credit: Customer (Accounts Payable)
	je.append("accounts", {
		"account": f"Creditors - {je.company}",  # Adjust account name as needed
		"party_type": "Customer",
		"party": claim.customer,
		"credit_in_account_currency": claim.approved_amount or claim.claim_amount
	})
	
	je.insert()
	
	# Link JE to claim
	claim.settlement_journal_entry = je.name
	claim.db_set('status', 'Settled', notify=True, commit=True)
	
	frappe.msgprint(f"Settlement Journal Entry {je.name} created successfully", alert=True, indicator="green")
	
	return je.name
