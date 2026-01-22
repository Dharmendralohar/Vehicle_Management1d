import frappe
from frappe import _
from frappe.utils import flt
import json

def validate_sales_order(doc, method):
    """
    Validate Sales Order as Insurance Proposal.
    Recalculates premium to prevent tampering and updates Item rate.
    """
    if not doc.get("is_insurance_proposal"):
        return

    from insurance_erp.insurance_erp.api.premium_calculator import calculate_premium
    
    addons = []
    if doc.proposal_addons:
        addons = [row.addon for row in doc.proposal_addons]
        
    calc = calculate_premium(doc.insurance_plan, doc.vehicle, doc.idv, addons, doc.ncb_percent)
    
    if not calc:
        return

    # 1. Update Breakdown Fields (Server side override to ensure correctness)
    doc.od_premium = calc.get("od_premium")
    doc.tp_premium = calc.get("tp_premium")
    doc.addon_premium = calc.get("addon_premium")
    doc.total_net_premium = calc.get("total_net_premium")
    doc.total_gst = calc.get("total_gst")
    doc.grand_total_premium = calc.get("grand_total_premium")
    
    # 2. Update Item Rate
    # Find the line item corresponding to Insurance Plan (assuming it matches the plan name or code)
    # Or just the first item if we enforce single item policy
    plan_item_found = False
    for item in doc.items:
        # Check if item code matches plan (if plan is item) or custom logic
        # For now, let's assume the user added the correct Item.
        # We update the FIRST item's rate to the Net Premium.
        # Ideally, we should check `item.item_code == doc.insurance_plan`.
        
        # If Plan Name matches Item Code (Common pattern)
        if item.item_code == doc.insurance_plan:
            item.rate = calc.get("total_net_premium")
            item.amount = item.rate * item.qty
            plan_item_found = True
            break
            
    if not plan_item_found and doc.items:
        # Fallback: Update the first item? Or warning?
        # Let's update the first item, assuming it is the insurance product.
        doc.items[0].rate = calc.get("total_net_premium")
        doc.items[0].amount = doc.items[0].rate * doc.items[0].qty

def before_insert_sales_invoice(doc, method):
    """
    On Creation of Sales Invoice from Sales Order (Insurance Proposal):
    1. Set is_insurance_policy = 1
    2. Generate Policy Number
    3. Snapshot Coverages
    4. Set Status
    """
    # 1. Identify if this is from an Insurance Proposal
    so_doc = None
    for item in doc.items:
        if item.sales_order:
            # Fetch SO (Optimization: Could use db.get_value but we need details for snapshot)
            try:
                so = frappe.get_doc("Sales Order", item.sales_order)
                if so.is_insurance_proposal:
                    so_doc = so
                    break
            except:
                pass
    
    if not so_doc:
        return

    doc.is_insurance_policy = 1
    doc.policy_status = "Pending Payment"
    
    # Copy Main Fields (if not mapped)
    doc.vehicle = so_doc.vehicle
    doc.idv = so_doc.idv
    doc.policy_start_date = so_doc.policy_duration_from
    doc.policy_end_date = so_doc.policy_duration_to
    
    # 2. Generate Policy Number
    settings = frappe.get_single("Insurance System Settings")
    series_pattern = settings.policy_naming_series or "POL-.YYYY.-.#####"
    from frappe.model.naming import make_autoname
    doc.policy_number = make_autoname(series_pattern)
    
    # 3. Snapshot Coverages
    if so_doc.insurance_plan:
        plan = frappe.get_doc("Insurance Plan", so_doc.insurance_plan)
        
        # A. Own Damage
        if plan.od_config_section: # Just checking existence/config
             # Using Limit=IDV for OD
             doc.append("coverage_snapshot", {
                 "coverage_type": "Own Damage",
                 "limit_type": "Percentage of IDV",
                 "limit_value": 100, # 100% of IDV
                 "deductible": plan.deductible_amount or 0
             })
             
        # B. Third Party
        doc.append("coverage_snapshot", {
             "coverage_type": "Third Party Liability",
             "limit_type": "Unlimited", # Usually unlimited for TP death/injury, fixed for property
             "limit_value": 0,
             "deductible": 0
        })
        
        # C. Add-ons
        # We need to look at SO Proposal Addons
        if so_doc.proposal_addons:
             for addon_row in so_doc.proposal_addons:
                 # Fetch addon config from Plan to see if there are limits?
                 # ideally we just list them.
                 doc.append("coverage_snapshot", {
                     "coverage_type": addon_row.addon,
                     "limit_type": "Fixed Amount", # Simplification
                     "limit_value": 0, # Depending on addon
                     "deductible": 0
                 })

def handle_payment_entry_submission(doc, method):
	"""
	Hooked to Payment Entry: After Submit
	Updates Sales Invoice (Policy) status to Active if fully paid.
	"""
	for ref in doc.get("references", []):
		if ref.reference_doctype == 'Sales Invoice':
			try:
				inv = frappe.get_doc('Sales Invoice', ref.reference_name)
				if not inv.get("is_insurance_policy"):
					continue
					
				# Check if fully paid
				# Payment Entry submission already updates Sales Invoice 'outstanding_amount' via standard ERPNext logic usually.
				# But to be safe or trigger specific status change:
				
				# Reload to get updated outstanding (after standard processing)
				inv.reload()
				
				if inv.outstanding_amount <= 0.1: # float tolerance
					inv.db_set('policy_status', 'Active', notify=True, commit=True)
					
					settings = frappe.get_single('Insurance System Settings')
					if settings.notify_customer_on_policy_activation:
						frappe.msgprint(_('Policy {0} has been activated').format(inv.policy_number), alert=True)
						
						if settings.notification_email_template:
						    # Fetch Customer Email
						    customer_email = frappe.db.get_value("Customer", inv.customer, "email_id")
						    if customer_email:
						        email_template = frappe.get_doc("Email Template", settings.notification_email_template)
						        message = frappe.render_template(email_template.response, {"doc": inv})
						        frappe.sendmail(
						            recipients=[customer_email],
						            subject=email_template.subject,
						            message=message,
						            reference_doctype=inv.doctype,
						            reference_name=inv.name
						        )
				else:
				    # Maybe set to Pending Payment if not?
				    pass
					
			except Exception:
				frappe.log_error(frappe.get_traceback(), _("Policy Activation Failed"))

def handle_journal_entry_submission(doc, method):
	"""
	Hooked to Journal Entry: After Submit
	Handles both Premium Receipts (for policies via SI) and Settlement Payments (for Claims).
	"""
	for row in doc.get("accounts", []):
		# 1. Handle Premium Receipt
		if row.reference_type == "Sales Invoice" and row.reference_name:
			try:
				inv = frappe.get_doc("Sales Invoice", row.reference_name)
				if inv.get("is_insurance_policy"):
				    inv.reload()
				    if inv.outstanding_amount <= 0.1:
				        inv.db_set('policy_status', 'Active', notify=True, commit=True)
			except Exception:
				frappe.log_error(frappe.get_traceback(), _("Policy Activation via JE Failed"))

		# 2. Handle Claim Settlement
		if row.reference_type == "Insurance Claim" and row.reference_name:
			try:
				claim = frappe.get_doc("Insurance Claim", row.reference_name)
				# Assuming settlement logic matches
				claim.db_set('claim_status', 'Settled', notify=True)
				claim.db_set('settlement_journal_entry', doc.name)
				frappe.db.commit()
				
				settings = frappe.get_single('Insurance System Settings')
				if settings.notify_customer_on_claim_status_change:
					frappe.msgprint(_('Claim {0} has been settled via JE {1}').format(claim.name, doc.name), alert=True)
			except Exception:
				frappe.log_error(frappe.get_traceback(), _("Claim Settlement via JE Failed"))
