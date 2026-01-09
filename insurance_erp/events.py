import frappe
from frappe import _

def handle_payment_entry_submission(doc, method):
	"""
	Hooked to Payment Entry: After Submit
	Updates Insurance Policy premium paid and activates it if fully paid.
	"""
	for ref in doc.get("references", []):
		if ref.reference_doctype == 'Insurance Policy':
			try:
				policy = frappe.get_doc('Insurance Policy', ref.reference_name)
				
				# Update paid amount using db_set
				new_paid_amount = float(policy.premium_paid or 0) + float(ref.allocated_amount or 0)
				policy.db_set('premium_paid', new_paid_amount)
				
				# Re-calculate outstanding
				new_outstanding = float(policy.premium_amount or 0) - new_paid_amount
				policy.db_set('outstanding_amount', new_outstanding)
				
				# Auto-activate if fully paid
				if new_outstanding <= 0:
					policy.db_set('status', 'Active', notify=True, commit=True)
					
					# Send notification if enabled
					settings = frappe.get_single('Insurance System Settings')
					if settings.notify_customer_on_policy_activation:
						frappe.msgprint(
							_('Policy {0} has been activated').format(policy.policy_number),
							indicator='green',
							alert=True
						)
				else:
					frappe.db.commit()
			except Exception as e:
				frappe.log_error(message=frappe.get_traceback(), title="Insurance Policy Payment Update Failed")

def handle_journal_entry_submission(doc, method):
	"""
	Hooked to Journal Entry: After Submit
	Updates Insurance Claim status to 'Settled' if it's a claim settlement JE.
	"""
	# Check if any account row links to Insurance Claim
	claim_name = None
	for row in doc.get("accounts", []):
		if row.reference_type == "Insurance Claim" and row.reference_name:
			claim_name = row.reference_name
			break

	if not claim_name and doc.user_remark and 'Claim Settlement' in doc.user_remark:
		# Fallback to remark check
		claim_name = frappe.db.get_value('Insurance Claim',
			{'settlement_journal_entry': doc.name},
			'name'
		)
		
	if claim_name:
		claim = frappe.get_doc('Insurance Claim', claim_name)
		claim.db_set('claim_status', 'Settled', notify=True, commit=True)
		claim.db_set('settlement_journal_entry', doc.name)
		
		# Send notification if enabled
		settings = frappe.get_single('Insurance System Settings')
		if settings.notify_customer_on_claim_status_change:
			frappe.msgprint(
				_('Claim {0} has been settled').format(claim.claim_number or claim.name),
				indicator='green',
				alert=True
			)
