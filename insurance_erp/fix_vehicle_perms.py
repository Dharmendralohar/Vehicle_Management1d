import frappe

def fix_vehicle_perms():
    doctype = "Vehicle"
    print(f"Cleaning up and restoring permissions for {doctype}...")
    
    # 1. Clear existing Custom DocPerm for Vehicle to start fresh
    frappe.db.delete("Custom DocPerm", {"parent": doctype})
    
    # 2. Add System Manager (Administrator) - Full Access
    print("Adding full access for System Manager...")
    frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": doctype,
        "parenttype": "DocType",
        "parentfield": "permissions",
        "role": "System Manager",
        "permlevel": 0,
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 1,
        "export": 1,
        "print": 1,
        "report": 1,
        "share": 1
    }).insert(ignore_permissions=True)
    
    # 3. Add Insurance Agent - Create and Write access
    print("Adding Create/Write access for Insurance Agent...")
    frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": doctype,
        "parenttype": "DocType",
        "parentfield": "permissions",
        "role": "Insurance Agent",
        "permlevel": 0,
        "read": 1,
        "write": 1,
        "create": 1,
        "delete": 1,
        "export": 1,
        "print": 1,
        "report": 1,
        "share": 1
    }).insert(ignore_permissions=True)
    
    # 4. Add Insurance Customer - Read only
    print("Adding Read access for Insurance Customer...")
    frappe.get_doc({
        "doctype": "Custom DocPerm",
        "parent": doctype,
        "parenttype": "DocType",
        "parentfield": "permissions",
        "role": "Insurance Customer",
        "permlevel": 0,
        "read": 1,
        "write": 0,
        "create": 0
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    frappe.clear_cache(doctype=doctype)
    print("\n✅ Permissions restored successfully for Vehicle.")

if __name__ == "__main__":
    fix_vehicle_perms()
