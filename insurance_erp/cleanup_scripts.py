import frappe

def cleanup_server_scripts():
    scripts_to_delete = [
        'Insurance Proposal - Validation',
        'Insurance Policy - Create from Proposal',
        'Insurance Policy - Activation on Payment',
        'Insurance Claim - Settlement Update'
    ]
    
    for script_name in scripts_to_delete:
        if frappe.db.exists('Server Script', script_name):
            print(f"Deleting Server Script: {script_name}")
            frappe.delete_doc('Server Script', script_name, ignore_missing=True)
    
    frappe.db.commit()
    frappe.clear_cache()
    print("Cleanup successful.")

if __name__ == "__main__":
    cleanup_server_scripts()
