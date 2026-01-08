import frappe

def force_schema_fix():
    # 1. Manually add status column if it doesn't exist
    columns = frappe.db.get_table_columns("Insurance Claim")
    if "status" not in columns:
        print("Adding 'status' column to 'tabInsurance Claim'...")
        frappe.db.sql("ALTER TABLE `tabInsurance Claim` ADD COLUMN status VARCHAR(255)")
    
    # 2. Sync data from claim_status
    if "claim_status" in columns:
        print("Syncing data from 'claim_status' to 'status'...")
        frappe.db.sql("""
            UPDATE `tabInsurance Claim` 
            SET status = claim_status 
            WHERE (status IS NULL OR status = '') 
            AND claim_status IS NOT NULL AND claim_status != ''
        """)
    
    # 3. Finalize
    frappe.db.commit()
    frappe.clear_cache()
    print("Schema fix and data sync completed.")

if __name__ == "__main__":
    force_schema_fix()
