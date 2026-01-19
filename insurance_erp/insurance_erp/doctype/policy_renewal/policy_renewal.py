import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate

class PolicyRenewal(Document):
    pass

def check_for_renewals():
    """Daily job to check for expiring policies"""
    # Expiry in 30 days
    target_date = add_days(frappe.utils.today(), 30)
    
    expiring_policies = frappe.get_all("Insurance Policy", 
        filters={
            "policy_end_date": target_date,
            "status": "Active"
        },
        fields=["name", "customer", "vehicle", "insurance_plan"]
    )
    
    for p in expiring_policies:
        create_renewal_proposal(p)

def create_renewal_proposal(policy_data):
    if frappe.db.exists("Insurance Proposal", {"amended_from": policy_data.name}):
        # Already created logic (simplistic check)
        return

    # Create new Proposal
    proposal = frappe.new_doc("Insurance Proposal")
    proposal.customer = policy_data.customer
    proposal.vehicle = policy_data.vehicle
    proposal.insurance_plan = policy_data.insurance_plan
    proposal.proposal_date = frappe.utils.today()
    proposal.policy_duration_from = add_days(policy_data.policy_end_date, 1) if hasattr(policy_data, 'policy_end_date') else frappe.utils.today()
    # proposal.policy_duration_to = ... (Need to calculate based on plan)
    
    # Just a stub for now
    proposal.save(ignore_permissions=True)
    frappe.log_error(f"Created Renewal Proposal {proposal.name}", "Renewal Job")
