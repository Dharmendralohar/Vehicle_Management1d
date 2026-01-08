# Direct Server Scripts Creation
# Creates server scripts directly in the database

import frappe

def create_server_scripts():
	"""Create all insurance server scripts"""
	
	scripts = [
		{
			"name": "Insurance Proposal - Validation",
			"script_type": "DocType Event",
			"reference_doctype": "Sales Order",
			"doctype_event": "Before Submit",
			"script": """# Validate Insurance Proposal before submission

if doc.is_insurance_proposal:
	# 1. Validate insurance item selected
	has_insurance_item = False
	for item in doc.items:
		item_doc = frappe.get_doc('Item', item.item_code)
		if item_doc.get('is_insurance_plan'):
			has_insurance_item = True
			break
	
	if not has_insurance_item:
		frappe.throw('Please select an Insurance Plan item')
	
	# 2. Validate vehicle is linked
	if not doc.vehicle:
		frappe.throw('Vehicle is mandatory for Insurance Proposal')
	
	# 3. Validate IDV variance (10% allowed)
	vehicle = frappe.get_doc('Vehicle', doc.vehicle)
	if abs(doc.vehicle_idv - vehicle.current_idv) / vehicle.current_idv > 0.1:
		frappe.throw('IDV variance exceeds 10% of vehicle current IDV')
	
	# 4. Validate policy duration
	if not doc.policy_duration_from or not doc.policy_duration_to:
		frappe.throw('Policy duration dates are mandatory')
	
	from dateutil.relativedelta import relativedelta
	from frappe.utils import getdate
	
	duration_start = getdate(doc.policy_duration_from)
	duration_end = getdate(doc.policy_duration_to)
	
	if duration_end < duration_start + relativedelta(months=11):
		frappe.throw('Minimum policy duration is 12 months')
	
	# 5. Validate customer matches vehicle customer
	if doc.customer != vehicle.customer:
		frappe.throw('Sales Order customer must match Vehicle customer')"""
		},
		{
			"name": "Insurance Policy - Create from Proposal",
			"script_type": "DocType Event",
			"reference_doctype": "Sales Invoice",
			"doctype_event": "Before Insert",
			"script": """# Auto-create policy from approved proposal

if doc.is_insurance_policy and doc.source_proposal:
	# Get the source proposal (Sales Order)
	proposal = frappe.get_doc('Sales Order', doc.source_proposal)
	
	# Validate proposal is approved
	if not proposal.get('is_insurance_proposal'):
		frappe.throw('Source Sales Order is not an Insurance Proposal')
	
	# Check workflow state if workflow exists
	workflow_state = proposal.get('workflow_state')
	if workflow_state and workflow_state not in ['Approved', 'Underwriter Approved']:
		frappe.throw(f'Can only create policy from Approved proposals. Current state: {workflow_state}')
	
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
			break"""
		},
		{
			"name": "Insurance Policy - Activation on Payment",
			"script_type": "DocType Event",
			"reference_doctype": "Payment Entry",
			"doctype_event": "After Submit",
			"script": """# Activate insurance policy when payment is received

for ref in doc.references:
	if ref.reference_doctype == 'Insurance Policy':
		policy = frappe.get_doc('Insurance Policy', ref.reference_name)
		
		# Update paid amount
		policy.premium_paid += ref.allocated_amount
		policy.save(ignore_permissions=True)
		
		# Auto-activate if fully paid
		if policy.outstanding_amount == 0:
			policy.db_set('status', 'Active', notify=True, commit=True)
			
			# Send notification if enabled
			settings = frappe.get_single('Insurance System Settings')
			if settings.notify_customer_on_policy_activation:
				frappe.msgprint(
					f'Policy {policy.policy_number} has been activated',
					indicator='green',
					alert=True
				)
	elif ref.reference_doctype == 'Sales Invoice':
		# Legacy support if still using invoices for some reason
		invoice = frappe.get_doc('Sales Invoice', ref.reference_name)
		if invoice.get('is_insurance_policy'):
			if invoice.outstanding_amount == 0:
				invoice.status = 'Active' # Already standardized
				invoice.save(ignore_permissions=True)"""
		},
		{
			"name": "Insurance Claim - Settlement Update",
			"script_type": "DocType Event",
			"reference_doctype": "Journal Entry",
			"doctype_event": "After Submit",
			"script": """# Update claim status when settlement JE is submitted

if doc.user_remark and 'Claim Settlement' in doc.user_remark:
	# Find linked insurance claim
	claim_name = frappe.db.get_value('Insurance Claim',
		{'settlement_journal_entry': doc.name},
		'name'
	)
	
	if claim_name:
		claim = frappe.get_doc('Insurance Claim', claim_name)
		claim.claim_status = 'Settled'
		claim.save(ignore_permissions=True)
		
		# Send notification if enabled
		settings = frappe.get_single('Insurance System Settings')
		if settings.notify_customer_on_claim_status_change:
			frappe.msgprint(
				f'Claim {claim.claim_number} has been settled',
				indicator='green',
				alert=True
			)"""
		}
	]
	
	print("\nCreating Server Scripts...")
	print("="*60)
	
	for script_data in scripts:
		existing = frappe.db.exists("Server Script", script_data["name"])
		
		if existing:
			doc = frappe.get_doc("Server Script", script_data["name"])
			doc.update(script_data)
			doc.save(ignore_permissions=True)
			print(f"✓ Updated: {script_data['name']}")
		else:
			doc = frappe.get_doc({
				"doctype": "Server Script",
				**script_data
			})
			doc.insert(ignore_permissions=True)
			print(f"✓ Created: {script_data['name']}")
	
	frappe.db.commit()
	frappe.clear_cache()
	 
	print("="*60)
	print("\n✅ All server scripts created successfully!\n")
	print("Server Scripts:")
	print("1. Sales Order - Validates insurance proposals before submission")
	print("2. Sales Invoice - Auto-creates policy from approved proposal")
	print("3. Payment Entry - Activates policy when fully paid")
	print("4. Journal Entry - Updates claim status to Settled")
	print("\nReload your desk to activate these scripts.")

if __name__ == "__main__":
	create_server_scripts()
