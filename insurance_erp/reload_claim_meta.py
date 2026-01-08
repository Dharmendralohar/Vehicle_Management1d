import frappe
from frappe.modules.import_file import import_file_by_path
import os

def reload_insurance_claim():
    # Path to the JSON file
    json_path = os.path.join(frappe.get_app_path('insurance_erp'), 'insurance_erp', 'doctype', 'insurance_claim', 'insurance_claim.json')
    
    if os.path.exists(json_path):
        print(f"Reloading Insurance Claim from {json_path}...")
        # Force reload from file to update tabDocField
        frappe.reload_doc('insurance_erp', 'doctype', 'insurance_claim', force=True)
        frappe.db.commit()
        
        # Verify if 'status' field exists in DocField now
        status_field = frappe.db.get_all('DocField', filters={'parent': 'Insurance Claim', 'fieldname': 'status'})
        if status_field:
            print("SUCCESS: 'status' field found in tabDocField.")
        else:
            print("ERROR: 'status' field still missing in tabDocField after reload.")
            
        # Also ensure 'claim_status' is removed from the UI if it was renamed
        legacy_field = frappe.db.get_all('DocField', filters={'parent': 'Insurance Claim', 'fieldname': 'claim_status'})
        if legacy_field:
            print("WARNING: 'claim_status' still exists in tabDocField. Cleaning it up...")
            frappe.db.sql("DELETE FROM `tabDocField` WHERE parent='Insurance Claim' AND fieldname='claim_status'")
            frappe.db.commit()
    else:
        print(f"ERROR: JSON file not found at {json_path}")

    frappe.clear_cache()
    print("Metadata cache cleared.")

if __name__ == "__main__":
    reload_insurance_claim()
