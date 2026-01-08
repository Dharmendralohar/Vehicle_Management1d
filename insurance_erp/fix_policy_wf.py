import frappe

def reset_policy_workflow():
    wf_name = "Insurance Policy Workflow"
    if not frappe.db.exists("Workflow", wf_name):
        print(f"Workflow '{wf_name}' not found.")
        return

    print(f"Standardizing {wf_name}...")
    
    # 0. Ensure Workflow States exist in master
    standard_states = [
        "Draft", "Pending Payment", "Active", 
        "Lapsed", "Cancelled", "Expired"
    ]
    
    for s_name in standard_states:
        if not frappe.db.exists("Workflow State", s_name):
            print(f"Creating Workflow State: {s_name}")
            frappe.get_doc({
                "doctype": "Workflow State",
                "workflow_state_name": s_name,
                "style": "Success" if s_name == "Active" else ""
            }).insert(ignore_permissions=True)

    # 1. Ensure Workflow Actions exist in master
    standard_actions = [
        "Submit", "Confirm Payment", "Cancel Policy", "Expire Policy"
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
    # (state, doc_status, allow_edit)
    # Note: Starting state is now Pending Payment
    states = [
        ("Pending Payment", 0, "Insurance Agent"),
        ("Active", 1, "Insurance Agent"),
        ("Lapsed", 1, "Insurance Agent"),
        ("Cancelled", 1, "Insurance Agent"),
        ("Expired", 1, "Insurance Agent")
    ]
    
    for state, docstatus, role in states:
        wf.append("states", {
            "state": state,
            "doc_status": docstatus,
            "allow_edit": role
        })
    
    # 3. Define Transitions
    transitions = [
        ("Confirm Payment", "Pending Payment", "Active", "Insurance Agent"),
        ("Cancel Policy", "Active", "Cancelled", "Insurance Agent"),
        ("Cancel Policy", "Pending Payment", "Cancelled", "Insurance Agent"),
        ("Expire Policy", "Active", "Expired", "Insurance Agent")
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
    
    # 4. Synchronize DocType options
    meta = frappe.get_meta("Insurance Policy")
    status_field = next((f for f in meta.fields if f.fieldname == "status"), None)
    if status_field:
        current_options = [o.strip() for o in (status_field.options or "").split("\n") if o.strip()]
        new_options = standard_states
        if set(current_options) != set(new_options):
            print("Updating DocType status options...")
            frappe.db.set_value("DocField", {"parent": "Insurance Policy", "fieldname": "status"}, "options", "\n".join(new_options))
            frappe.clear_cache(doctype="Insurance Policy")

    frappe.db.commit()
    frappe.clear_cache()
    print("Workflow and DocType options standardized successfully for Insurance Policy.")

if __name__ == "__main__":
    reset_policy_workflow()
