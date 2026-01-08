import frappe

def reset_claim_workflow():
    wf_name = "Insurance Claim Workflow"
    if not frappe.db.exists("Workflow", wf_name):
        print(f"Workflow '{wf_name}' not found.")
        return

    # 0. Ensure Workflow States exist in master
    standard_states = [
        "Reported", "Survey Assigned", "Survey Completed", 
        "Verification Assigned", "Agent Verified", 
        "Approved", "Rejected", "Settled"
    ]
    
    for s_name in standard_states:
        if not frappe.db.exists("Workflow State", s_name):
            print(f"Creating Workflow State: {s_name}")
            frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": s_name,
                "style": "Primary" if s_name in ["Approved", "Settled"] else ""
            }).insert(ignore_permissions=True)

    # 1. Ensure Workflow Actions exist in master
    standard_actions = [
        "Assign Surveyor", "Submit Survey", "Assign Verification", 
        "Verify Claim", "Approve Claim", "Reject Claim", 
        "Approve Directly", "Reject Directly", "Settle Claim"
    ]
    
    for a_name in standard_actions:
        if not frappe.db.exists("Workflow Action Master", a_name):
            print(f"Creating Workflow Action: {a_name}")
            frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": a_name
            }).insert(ignore_permissions=True)

    print(f"Resetting {wf_name}...")
    wf = frappe.get_doc("Workflow", wf_name)
    
    # Clear existing states and transitions
    wf.states = []
    wf.transitions = []
    
    # 2. Define Standard States
    # (state, doc_status, allow_edit)
    # Note: Reported is the NEW starting state (replacing Open)
    states = [
        ("Reported", 0, "Claims Officer"),
        ("Survey Assigned", 0, "Claims Officer"),
        ("Survey Completed", 0, "Claims Officer"),
        ("Verification Assigned", 0, "Claims Officer"),
        ("Agent Verified", 0, "Claims Officer"),
        ("Approved", 1, "Claims Officer"),
        ("Rejected", 1, "Claims Officer"),
        ("Settled", 1, "Claims Officer")
    ]
    
    for state, docstatus, role in states:
        wf.append("states", {
            "state": state,
            "doc_status": docstatus,
            "allow_edit": role
        })
    
    # 3. Define Transitions
    transitions = [
        ("Assign Surveyor", "Reported", "Survey Assigned", "Claims Officer"),
        ("Submit Survey", "Survey Assigned", "Survey Completed", "Surveyor"),
        ("Assign Verification", "Survey Completed", "Verification Assigned", "Claims Officer"),
        ("Verify Claim", "Verification Assigned", "Agent Verified", "Claims Officer"),
        ("Approve Claim", "Agent Verified", "Approved", "Claims Officer"),
        ("Reject Claim", "Agent Verified", "Rejected", "Claims Officer"),
        ("Approve Directly", "Survey Completed", "Approved", "Claims Officer"),
        ("Reject Directly", "Survey Completed", "Rejected", "Claims Officer"),
        ("Settle Claim", "Approved", "Settled", "Claims Officer")
    ]
    
    for action, state, next_state, role in transitions:
        wf.append("transitions", {
            "action": action,
            "state": state,
            "next_state": next_state,
            "allowed": role
        })

    wf.workflow_state_field = "status"
    wf.is_active = 1
    wf.save(ignore_permissions=True)
    
    frappe.db.commit()
    frappe.clear_cache()
    print("Workflow reset and standardized successfully.")

if __name__ == "__main__":
    reset_claim_workflow()
