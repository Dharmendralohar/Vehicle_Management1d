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
				
				# Update paid amount using db_set to bypass Workflow locks
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
					frappe.db.commit() # Ensure premium_paid is saved
			except Exception as e:
				frappe.log_error(message=frappe.get_traceback(), title="Insurance Policy Payment Update Failed")
		
		elif ref.reference_doctype == 'Sales Invoice':
			# Legacy support for ERPNext standard docs tagged as insurance
			invoice = frappe.get_doc('Sales Invoice', ref.reference_name)
			if invoice.get('is_insurance_policy'):
				if invoice.outstanding_amount <= 0:
					invoice.db_set('status', 'Active', notify=True, commit=True)

def handle_journal_entry_submission(doc, method):
	"""
	Hooked to Journal Entry: After Submit
	Updates Insurance Claim status to 'Settled' if it's a claim settlement JE.
	"""
	if doc.user_remark and 'Claim Settlement' in doc.user_remark:
		# Find linked insurance claim
		claim_name = frappe.db.get_value('Insurance Claim',
			{'settlement_journal_entry': doc.name},
			'name'
		)
		
		if claim_name:
			claim = frappe.get_doc('Insurance Claim', claim_name)
			claim.db_set('claim_status', 'Settled', notify=True, commit=True)
			
			# Send notification if enabled
			settings = frappe.get_single('Insurance System Settings')
			if settings.notify_customer_on_claim_status_change:
				frappe.msgprint(
					_('Claim {0} has been settled').format(claim.claim_number),
					indicator='green',
					alert=True
				)

def handle_sales_order_before_submit(doc, method):
	"""
	Hooked to Sales Order: Before Submit
	Validates insurance proposal if flag is set.
	"""
	if doc.get('is_insurance_proposal'):
		# 1. Validate insurance item selected
		has_insurance_item = False
		for item in doc.items:
			item_doc = frappe.get_doc('Item', item.item_code)
			if item_doc.get('is_insurance_plan'):
				has_insurance_item = True
				break
		
		if not has_insurance_item:
			frappe.throw(_('Please select an Insurance Plan item'))
		
		# 2. Validate vehicle is linked
		if not doc.get('vehicle'):
			frappe.throw(_('Vehicle is mandatory for Insurance Proposal'))
		
		# 3. Validate IDV variance (10% allowed)
		vehicle = frappe.get_doc('Vehicle', doc.vehicle)
		if abs(doc.get('vehicle_idv') - vehicle.current_idv) / vehicle.current_idv > 0.1:
			frappe.throw(_('IDV variance exceeds 10% of vehicle current IDV'))
		
		# 4. Validate policy duration
		if not doc.get('policy_duration_from') or not doc.get('policy_duration_to'):
			frappe.throw(_('Policy duration dates are mandatory'))
		
		from dateutil.relativedelta import relativedelta
		from frappe.utils import getdate
		
		duration_start = getdate(doc.policy_duration_from)
		duration_end = getdate(doc.policy_duration_to)
		
		if duration_end < duration_start + relativedelta(months=11):
			frappe.throw(_('Minimum policy duration is 12 months'))
		
		# 5. Validate customer matches vehicle customer
		if doc.customer != vehicle.customer:
			frappe.throw(_('Sales Order customer must match Vehicle customer'))

def handle_sales_invoice_before_insert(doc, method):
	"""
	Hooked to Sales Invoice: Before Insert
	Auto-creates policy fields from proposal if flag is set.
	"""
	if doc.get('is_insurance_policy') and doc.get('source_proposal'):
		# Get the source proposal (Sales Order)
		proposal = frappe.get_doc('Sales Order', doc.source_proposal)
		
		# Validate proposal is approved
		if not proposal.get('is_insurance_proposal'):
			frappe.throw(_('Source Sales Order is not an Insurance Proposal'))
		
		# Check workflow state if workflow exists
		workflow_state = proposal.get('workflow_state')
		if workflow_state and workflow_state not in ['Approved', 'Underwriter Approved']:
			frappe.throw(_('Can only create policy from Approved proposals. Current state: {0}').format(workflow_state))
		
		# Generate policy number from settings
		settings = frappe.get_single('Insurance System Settings')
		doc.policy_number = frappe.model.naming.make_autoname(settings.policy_naming_series)
		
		# Copy vehicle and IDV from proposal
		doc.vehicle = proposal.vehicle
		doc.vehicle_idv = proposal.vehicle_idv
		doc.policy_start_date = proposal.policy_duration_from
		doc.policy_end_date = proposal.policy_duration_to
		doc.status = 'Pending Payment'
		
		# Freeze coverage snapshot from insurance plan item
		for item in proposal.items:
			item_doc = frappe.get_doc('Item', item.item_code)
			if item_doc.get('is_insurance_plan'):
				# Copy coverage types to snapshot
				for coverage in item_doc.get('coverage_types', []):
					doc.append('coverage_snapshot', {
						'coverage_type': coverage.coverage_type,
						'limit_type': coverage.limit_type,
						'limit_value': coverage.limit_value,
						'deductible': coverage.deductible
					})
				break

@frappe.whitelist()
def create_payment_for_policy(policy_name, mode_of_payment, amount, paid_to=None, reference_no=None, reference_date=None):
	"""
	Creates and submits a Payment Entry for an Insurance Policy.
	Bypasses Client Script errors by doing it server-side.
	"""
	policy = frappe.get_doc("Insurance Policy", policy_name)
	
	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Receive"
	pe.party_type = "Customer"
	pe.party = policy.customer
	pe.company = policy.get("company") or frappe.db.get_default("company")
	pe.mode_of_payment = mode_of_payment
	
	# If paid_to is not provided, try to fetch default from Mode of Payment or Company
	if not paid_to:
		mop = frappe.get_doc("Mode of Payment", mode_of_payment)
		for account in mop.accounts:
			if account.company == pe.company:
				paid_to = account.default_account
				break
	
	if not paid_to:
		frappe.throw(_("Please select a 'Paid To' account or set a default account for {0}").format(mode_of_payment))
		
	pe.paid_to = paid_to
	pe.paid_amount = float(amount)
	pe.received_amount = float(amount)
	pe.reference_no = reference_no or policy.name
	pe.reference_date = reference_date or frappe.utils.today()
	
	pe.append("references", {
		"reference_doctype": "Insurance Policy",
		"reference_name": policy.name,
		"total_amount": policy.premium_amount,
		"outstanding_amount": policy.outstanding_amount,
		"allocated_amount": float(amount)
	})
	
	pe.insert(ignore_permissions=True)
	pe.submit()
	
	return pe.name

@frappe.whitelist()
def assign_surveyor_to_claims(claim_names, surveyor, survey_date=None):
	"""
	Bulk transitions claims to 'Survey Assigned' and creates Claim Survey records.
	Called from Insurance Claim List View.
	"""
	if isinstance(claim_names, str):
		import json
		claim_names = json.loads(claim_names)
	
	results = []
	for name in claim_names:
		try:
			claim = frappe.get_doc("Insurance Claim", name)
			
			# 1. Create the Survey record
			survey = frappe.new_doc("Claim Survey")
			survey.claim = name
			survey.surveyor = surveyor
			survey.survey_date = survey_date or frappe.utils.today()
			survey.insert(ignore_permissions=True)
			
			# 2. Update claim status and link survey
			claim.db_set('status', 'Survey Assigned')
			claim.db_set('survey', survey.name)
			
			results.append({"status": "Success", "claim": name, "survey": survey.name})
		except Exception as e:
			frappe.log_error(message=frappe.get_traceback(), title=f"Survey Assignment Failed for {name}")
			results.append({"status": "Error", "claim": name, "message": str(e)})
	
	return results
