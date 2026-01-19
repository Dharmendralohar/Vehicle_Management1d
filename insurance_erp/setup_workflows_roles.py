import frappe
from frappe import _

def create_workflow_states():
    states = [
        "Draft", "Submitted", "Underwriting", "Approved", "Rejected",
        "Reported", "Survey Assigned", "Survey Completed", "Verification Assigned",
        "Agent Verified", "Settled"
    ]
    for state in states:
        if not frappe.db.exists("Workflow State", state):
            frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": state,
                "style": "Primary" if state in ["Approved", "Settled"] else ""
            }).insert(ignore_permissions=True)

def create_workflow_actions():
    actions = [
        "Submit", "Review", "Approve", "Reject", "Assign Survey",
        "Complete Survey", "Assign Verification", "Verify", "Settle"
    ]
    for action in actions:
        if not frappe.db.exists("Workflow Action Master", action):
            frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": action
            }).insert(ignore_permissions=True)

def create_proposal_workflow():
    if not frappe.db.exists("Workflow", "Insurance Proposal Workflow"):
        wf = frappe.new_doc("Workflow")
        wf.workflow_name = "Insurance Proposal Workflow"
        wf.document_type = "Insurance Proposal"
        wf.workflow_state_field = "status"
        wf.is_active = 1
        
        # States
        wf.append("states", {"state": "Draft", "doc_status": 0, "allow_edit": "Insurance Agent"})
        wf.append("states", {"state": "Submitted", "doc_status": 0, "allow_edit": "Insurance Agent"})
        wf.append("states", {"state": "Underwriting", "doc_status": 0, "allow_edit": "Insurance Underwriter"})
        wf.append("states", {"state": "Approved", "doc_status": 1, "allow_edit": "Insurance Underwriter"})
        wf.append("states", {"state": "Rejected", "doc_status": 1, "allow_edit": "Insurance Underwriter"})
        
        # Transitions
        wf.append("transitions", {"state": "Draft", "action": "Submit", "next_state": "Submitted", "allowed": "Insurance Agent"})
        wf.append("transitions", {"state": "Submitted", "action": "Review", "next_state": "Underwriting", "allowed": "Insurance Underwriter"})
        wf.append("transitions", {"state": "Underwriting", "action": "Approve", "next_state": "Approved", "allowed": "Insurance Underwriter"})
        wf.append("transitions", {"state": "Underwriting", "action": "Reject", "next_state": "Rejected", "allowed": "Insurance Underwriter"})
        
        wf.insert(ignore_permissions=True)

def create_claim_workflow():
    if not frappe.db.exists("Workflow", "Insurance Claim Workflow"):
        wf = frappe.new_doc("Workflow")
        wf.workflow_name = "Insurance Claim Workflow"
        wf.document_type = "Insurance Claim"
        wf.workflow_state_field = "claim_status"
        wf.is_active = 1
        
        # States
        wf.append("states", {"state": "Reported", "doc_status": 0, "allow_edit": "Insurance Agent"})
        wf.append("states", {"state": "Survey Assigned", "doc_status": 0, "allow_edit": "Claims Officer"})
        wf.append("states", {"state": "Survey Completed", "doc_status": 0, "allow_edit": "Surveyor"})
        wf.append("states", {"state": "Verification Assigned", "doc_status": 0, "allow_edit": "Claims Officer"})
        wf.append("states", {"state": "Agent Verified", "doc_status": 0, "allow_edit": "Claim Verification Agent"})
        wf.append("states", {"state": "Approved", "doc_status": 1, "allow_edit": "Claims Officer"})
        wf.append("states", {"state": "Rejected", "doc_status": 1, "allow_edit": "Claims Officer"})
        wf.append("states", {"state": "Settled", "doc_status": 1, "allow_edit": "Finance User"})
        
        # Transitions
        wf.append("transitions", {"state": "Reported", "action": "Assign Survey", "next_state": "Survey Assigned", "allowed": "Claims Officer"})
        wf.append("transitions", {"state": "Survey Assigned", "action": "Complete Survey", "next_state": "Survey Completed", "allowed": "Surveyor"})
        wf.append("transitions", {"state": "Survey Completed", "action": "Assign Verification", "next_state": "Verification Assigned", "allowed": "Claims Officer"})
        wf.append("transitions", {"state": "Verification Assigned", "action": "Verify", "next_state": "Agent Verified", "allowed": "Claim Verification Agent"})
        wf.append("transitions", {"state": "Agent Verified", "action": "Approve", "next_state": "Approved", "allowed": "Claims Officer"})
        wf.append("transitions", {"state": "Agent Verified", "action": "Reject", "next_state": "Rejected", "allowed": "Claims Officer"})
        wf.append("transitions", {"state": "Approved", "action": "Settle", "next_state": "Settled", "allowed": "Finance User"})
        
        wf.insert(ignore_permissions=True)

def create_roles():
    roles = [
        "Insurance System Admin",
        "Insurance Agent",
        "Insurance Underwriter",
        "Claims Officer",
        "Surveyor",
        "Claim Verification Agent",
        "Finance User",
        "Insurance Customer"
    ]
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role}).insert(ignore_permissions=True)

def main():
    create_roles()
    create_workflow_states()
    create_workflow_actions()
    create_proposal_workflow()
    create_claim_workflow()
    print("Workflows and Roles setup complete.")

if __name__ == "__main__":
    main()
