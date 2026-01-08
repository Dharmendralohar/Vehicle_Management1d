import frappe

def fix_claim_status_and_workflow():
    # 1. Update existing claims to move data to 'status' field if needed
    frappe.db.sql("""
        UPDATE `tabInsurance Claim` 
        SET status = claim_status 
        WHERE (status IS NULL OR status = '') 
        AND claim_status IS NOT NULL AND claim_status != ''
    """)
    
    # 2. Update Workflow
    wf_name = "Insurance Claim Workflow"
    if frappe.db.exists("Workflow", wf_name):
        wf = frappe.get_doc("Workflow", wf_name)
        wf.workflow_state_field = "status"
        wf.is_active = 1
        
        # Ensure transitions use the correct field if any logic depends on it
        # (Usually transitions depend on the current state)
        
        wf.save(ignore_permissions=True)
        print(f"Workflow '{wf_name}' updated and activated.")
    
    frappe.db.commit()
    frappe.clear_cache()
    print("Claim status and workflow synchronization complete.")

if __name__ == "__main__":
    fix_claim_status_and_workflow()
