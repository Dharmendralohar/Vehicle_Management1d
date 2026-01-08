import frappe

def reset_proposal_workflow():
    wf_name = "Insurance Proposal Workflow"
    if not frappe.db.exists("Workflow", wf_name):
        print(f"Workflow '{wf_name}' not found.")
        return

    print(f"Standardizing {wf_name}...")
    
    # 0. Ensure Workflow States exist in master
    standard_states = [
        "Draft", "Submitted", "Under Review", 
        "Underwriting", "Approved", "Rejected"
    ]
    
    for s_name in standard_states:
        if not frappe.db.exists("Workflow State", s_name):
            print(f"Creating Workflow State: {s_name}")
            frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": s_name,
                "style": "Primary" if s_name in ["Approved"] else ""
            }).insert(ignore_permissions=True)

    # 1. Ensure Workflow Actions exist in master
    standard_actions = [
        "Submit", "Start Review", "Start Underwriting", 
        "Approve", "Reject"
    ]
    
    for a_name in standard_actions:
        if not frappe.db.exists("Workflow Action Master", a_name):
            print(f"Creating Workflow Action: {a_name}")
            frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": a_name
            }).insert(ignore_permissions=True)

    wf = frappe.get_doc("Workflow", wf_name)
    
    # Reset states and transitions
    wf.states = []
    wf.transitions = []
    
    # 2. Define Standard States
    states = [
        ("Draft", 0, "Insurance Agent"),
        ("Submitted", 0, "Insurance Underwriter"),
        ("Under Review", 0, "Insurance Underwriter"),
        ("Underwriting", 0, "Insurance Underwriter"),
        ("Approved", 1, "Insurance Underwriter"),
        ("Rejected", 1, "Insurance Underwriter")
    ]
    
    for state, docstatus, role in states:
        wf.append("states", {
            "state": state,
            "doc_status": docstatus,
            "allow_edit": role
        })
    
    # 3. Define Transitions
    transitions = [
        ("Submit for Review", "Draft", "Under Review", "Insurance Agent"),
        ("Submit", "Draft", "Submitted", "Insurance Agent"),
        ("Start Review", "Submitted", "Under Review", "Insurance Underwriter"),
        ("Start Underwriting", "Under Review", "Underwriting", "Insurance Underwriter"),
        ("Approve", "Underwriting", "Approved", "Insurance Underwriter"),
        ("Reject", "Underwriting", "Rejected", "Insurance Underwriter"),
        ("Approve Directly", "Submitted", "Approved", "Insurance Underwriter"),
        ("Reject Directly", "Submitted", "Rejected", "Insurance Underwriter"),
        ("Approve Directly", "Under Review", "Approved", "Insurance Underwriter"),
        ("Reject Directly", "Under Review", "Rejected", "Insurance Underwriter")
    ]
    
    for action, state, next_state, role in transitions:
        # Action Master Check
        if not frappe.db.exists("Workflow Action Master", action):
             frappe.get_doc({
                "doctype": "Workflow Action Master",
                "workflow_action_name": action
            }).insert(ignore_permissions=True)

        wf.append("transitions", {
            "action": action,
            "state": state,
            "next_state": next_state,
            "allowed": role
        })

    wf.workflow_state_field = "status"
    wf.is_active = 1
    wf.save(ignore_permissions=True)
    
    # 4. Synchronize DocType options
    meta = frappe.get_meta("Insurance Proposal")
    status_field = next((f for f in meta.fields if f.fieldname == "status"), None)
    if status_field:
        current_options = [o.strip() for o in (status_field.options or "").split("\n") if o.strip()]
        new_options = standard_states
        if set(current_options) != set(new_options):
            print("Updating DocType status options...")
            frappe.db.set_value("DocField", {"parent": "Insurance Proposal", "fieldname": "status"}, "options", "\n".join(new_options))
            frappe.clear_cache(doctype="Insurance Proposal")

    frappe.db.commit()
    frappe.clear_cache()
    print("Workflow and DocType options standardized successfully.")

if __name__ == "__main__":
    reset_proposal_workflow()
