import frappe
from frappe import _

def create_proposal_workflow():
    if not frappe.db.exists("Workflow", "Insurance Proposal Workflow"):
        wf = frappe.new_doc("Workflow")
        wf.workflow_name = "Insurance Proposal Workflow"
        wf.document_type = "Insurance Proposal"
        wf.workflow_state_field = "workflow_state"
        wf.is_active = 1
        
        # States
        wf.append("states", {"state": "Draft", "doc_status": 0, "allow_edit": "Insurance Agent"})
        wf.append("states", {"state": "Submitted", "doc_status": 1, "allow_edit": "Insurance Underwriter"})
        wf.append("states", {"state": "Approved", "doc_status": 1, "allow_edit": "Insurance Underwriter"})
        wf.append("states", {"state": "Rejected", "doc_status": 1, "allow_edit": "Insurance Underwriter"})
        
        # Transitions
        wf.append("transitions", {"state": "Draft", "action": "Submit", "next_state": "Submitted", "allowed": "Insurance Agent"})
        wf.append("transitions", {"state": "Submitted", "action": "Approve", "next_state": "Approved", "allowed": "Insurance Underwriter"})
        wf.append("transitions", {"state": "Submitted", "action": "Reject", "next_state": "Rejected", "allowed": "Insurance Underwriter"})
        
        wf.insert(ignore_permissions=True)
        print("Insurance Proposal Workflow created.")

def create_claim_workflow():
    if not frappe.db.exists("Workflow", "Insurance Claim Workflow"):
        wf = frappe.new_doc("Workflow")
        wf.workflow_name = "Insurance Claim Workflow"
        wf.document_type = "Insurance Claim"
        wf.workflow_state_field = "claim_status"
        wf.is_active = 1
        
        # States (matching the Select options in doctype)
        wf.append("states", {"state": "Reported", "doc_status": 0, "allow_edit": "Insurance Agent"})
        wf.append("states", {"state": "Survey Assigned", "doc_status": 0, "allow_edit": "Claims Officer"})
        wf.append("states", {"state": "Survey Completed", "doc_status": 0, "allow_edit": "Surveyor"})
        wf.append("states", {"state": "Verification Assigned", "doc_status": 0, "allow_edit": "Claims Officer"})
        wf.append("states", {"state": "Agent Verified", "doc_status": 0, "allow_edit": "Claim Verification Agent"})
        wf.append("states", {"state": "Approved", "doc_status": 1, "allow_edit": "Claims Officer"})
        wf.append("states", {"state": "Rejected", "doc_status": 1, "allow_edit": "Claims Officer"})
        wf.append("states", {"state": "Settled", "doc_status": 1, "allow_edit": "Finance & Accounts"})
        
        # Transitions
        wf.append("transitions", {"state": "Reported", "action": "Assign Survey", "next_state": "Survey Assigned", "allowed": "Claims Officer"})
        wf.append("transitions", {"state": "Survey Assigned", "action": "Complete Survey", "next_state": "Survey Completed", "allowed": "Surveyor"})
        wf.append("transitions", {"state": "Survey Completed", "action": "Assign Verification", "next_state": "Verification Assigned", "allowed": "Claims Officer"})
        wf.append("transitions", {"state": "Verification Assigned", "action": "Verify", "next_state": "Agent Verified", "allowed": "Claim Verification Agent"})
        wf.append("transitions", {"state": "Agent Verified", "action": "Approve", "next_state": "Approved", "allowed": "Claims Officer"})
        wf.append("transitions", {"state": "Agent Verified", "action": "Reject", "next_state": "Rejected", "allowed": "Claims Officer"})
        wf.append("transitions", {"state": "Approved", "action": "Settle", "next_state": "Settled", "allowed": "Finance & Accounts"})
        
        wf.insert(ignore_permissions=True)
        print("Insurance Claim Workflow created.")

def create_roles():
    roles = [
        "Insurance System Admin",
        "Insurance Agent",
        "Insurance Underwriter",
        "Claims Officer",
        "Surveyor",
        "Claim Verification Agent",
        "Finance & Accounts",
        "Insurance Customer"
    ]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)
            print(f"Role {role} created.")

if __name__ == "__main__":
    create_roles()
    create_proposal_workflow()
    create_claim_workflow()
