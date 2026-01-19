import frappe
from frappe import _
from frappe.utils import flt
import json

def handle_payment_entry_submission(doc, method):
	"""
	Hooked to Payment Entry: After Submit
	Updates Insurance Policy premium paid and activates it if fully paid.
	"""
	for ref in doc.get("references", []):
		if ref.reference_doctype == 'Insurance Policy':
			try:
				policy = frappe.get_doc('Insurance Policy', ref.reference_name)
				paid_amount = flt(policy.premium_paid or 0) + flt(ref.allocated_amount or 0)
				policy.db_set('premium_paid', paid_amount)
				
				total = flt(policy.total_premium_payable or 0)
				outstanding = total - paid_amount
				policy.db_set('outstanding_amount', outstanding)
				
				if outstanding <= 0 and total > 0:
					policy.db_set('status', 'Active', notify=True, commit=True)
					settings = frappe.get_single('Insurance System Settings')
					if settings.notify_customer_on_policy_activation:
						frappe.msgprint(_('Policy {0} has been activated').format(policy.name), alert=True)
				else:
					frappe.db.commit()
			except Exception:
				frappe.log_error(frappe.get_traceback(), _("Insurance Policy Payment Update Failed"))

def handle_journal_entry_submission(doc, method):
	"""
	Hooked to Journal Entry: After Submit
	Handles both Premium Receipts (for Policies) and Settlement Payments (for Claims).
	"""
	for row in doc.get("accounts", []):
		# 1. Handle Premium Receipt
		if row.reference_type == "Insurance Policy" and row.reference_name:
			try:
				policy = frappe.get_doc("Insurance Policy", row.reference_name)
				amount = flt(row.credit) if flt(row.credit) > 0 else flt(row.debit)
				
				paid_amount = flt(policy.premium_paid or 0) + amount
				policy.db_set('premium_paid', paid_amount)
				
				total = flt(policy.total_premium_payable or 0)
				outstanding = total - paid_amount
				policy.db_set('outstanding_amount', outstanding)
				
				if outstanding <= 0 and total > 0:
					policy.db_set('status', 'Active', notify=True)
				
				frappe.db.commit()
			except Exception:
				frappe.log_error(frappe.get_traceback(), _("Policy Premium Update via JE Failed"))

		# 2. Handle Claim Settlement
		if row.reference_type == "Insurance Claim" and row.reference_name:
			try:
				claim = frappe.get_doc("Insurance Claim", row.reference_name)
				claim.db_set('claim_status', 'Settled', notify=True)
				claim.db_set('settlement_journal_entry', doc.name)
				frappe.db.commit()
				
				settings = frappe.get_single('Insurance System Settings')
				if settings.notify_customer_on_claim_status_change:
					frappe.msgprint(_('Claim {0} has been settled via JE {1}').format(claim.name, doc.name), alert=True)
			except Exception:
				frappe.log_error(frappe.get_traceback(), _("Claim Settlement via JE Failed"))

def validate_journal_entry(doc, method):
	"""
	Hooked to Journal Entry: Before Submit
	Ensures that if a row references an Insurance Policy or Claim, 
	critical fields are present.
	"""
	for row in doc.get("accounts", []):
		if row.reference_type == "Insurance Policy" and row.reference_name:
			policy = frappe.get_doc("Insurance Policy", row.reference_name)
			if not policy.total_premium_payable:
				frappe.throw(_("Cannot post Journal Entry for Policy {0} as its Total Premium Payable is missing.").format(policy.name))
		
		if row.reference_type == "Insurance Claim" and row.reference_name:
			claim = frappe.get_doc("Insurance Claim", row.reference_name)
			if not claim.claim_status in ["Approved", "Settled"]:
				frappe.throw(_("Cannot post Journal Entry for Claim {0} unless it is in Approved or Settled status.").format(claim.name))

@frappe.whitelist()
def create_payment_for_policy(policy_name, mode_of_payment, paid_to, amount, reference_no=None, reference_date=None):
	"""
	Creates a Payment Entry for an Insurance Policy.
	Called from Insurance Policy custom button 'Record Payment'.
	"""
	policy = frappe.get_doc("Insurance Policy", policy_name)
	
	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Receive"
	pe.party_type = "Customer"
	pe.party = policy.customer
	pe.paid_to = paid_to
	pe.mode_of_payment = mode_of_payment
	pe.paid_amount = flt(amount)
	pe.received_amount = flt(amount)
	pe.reference_no = reference_no or policy.name
	pe.reference_date = reference_date or frappe.utils.today()
	
	# Add Reference to Policy
	pe.append("references", {
		"reference_doctype": "Insurance Policy",
		"reference_name": policy.name,
		"allocated_amount": flt(amount)
	})
	
	pe.insert(ignore_permissions=True)
	pe.submit()
	
	return pe.name
