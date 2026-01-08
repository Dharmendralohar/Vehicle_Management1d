import frappe

def fix_claim_workflow():
    wf_name = "Insurance Claim Workflow"
    if not frappe.db.exists("Workflow", wf_name):
        print(f"Workflow {wf_name} not found.")
        return
        
    print(f"Fixing {wf_name}...")
    wf = frappe.get_doc("Workflow", wf_name)
    
    # Define States and their correct docstatus
    # terminal states of submittable doctypes should be 1
    state_status_map = {
        "Reported": 1,
        "Survey Assigned": 1,
        "Survey Completed": 1,
        "Verification Assigned": 1,
        "Agent Verified": 1,
        "Approved": 1,
        "Rejected": 1,
        "Settled": 1,
        "Completed": 1
    }
    
    updated = False
    for s in wf.states:
        if s.state in state_status_map:
            if s.doc_status != state_status_map[s.state]:
                print(f"Updating State: {s.state} DocStatus: {s.doc_status} -> {state_status_map[s.state]}")
                s.doc_status = state_status_map[s.state]
                updated = True
        
    # 2. Synchronize DocType options via Property Setter (more robust)
    print("Updating DocType status options via Property Setter...")
    new_options = "\n".join(state_status_map.keys())
    
    from frappe.custom.doctype.property_setter.property_setter import make_property_setter
    make_property_setter(
        "Insurance Claim", 
        "status", 
        "options", 
        new_options, 
        "Select", 
        validate_fields_for_doctype=True
    )

    frappe.db.commit()
    frappe.clear_cache(doctype="Insurance Claim")
    frappe.clear_cache()
    print("Workflow and DocType options standardized successfully for Insurance Claim.")

if __name__ == "__main__":
    fix_claim_workflow()
