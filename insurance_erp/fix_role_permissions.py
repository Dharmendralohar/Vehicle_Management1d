import frappe

def add_custom_permission(doctype, role, permlevel=0, **kwargs):
    if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role, "permlevel": permlevel}):
        print(f"Adding permission for {role} on {doctype}...")
        perm = frappe.get_doc({
            "doctype": "Custom DocPerm",
            "parent": doctype,
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": role,
            "permlevel": permlevel,
            "read": kwargs.get("read", 1),
            "write": kwargs.get("write", 0),
            "create": kwargs.get("create", 0),
            "delete": kwargs.get("delete", 0),
            "submit": kwargs.get("submit", 0),
            "cancel": kwargs.get("cancel", 0),
            "amend": kwargs.get("amend", 0),
            "export": kwargs.get("export", 0),
            "print": kwargs.get("print", 0),
            "report": kwargs.get("report", 0)
        })
        perm.insert(ignore_permissions=True)
    else:
        print(f"Permission for {role} on {doctype} already exists.")

def fix_all_permissions():
    print("Fixing Insurance Role Permissions...")
    
    # 1. Insurance Agent
    add_custom_permission("Insurance Claim", "Insurance Agent", read=1, write=1, create=1, submit=1)
    add_custom_permission("Insurance Policy", "Insurance Agent", read=1, write=1, submit=1)
    add_custom_permission("Vehicle", "Insurance Agent", read=1)
    add_custom_permission("Customer", "Insurance Agent", read=1)
    
    # 2. Surveyor
    add_custom_permission("Insurance Claim", "Surveyor", read=1)
    add_custom_permission("Claim Survey", "Surveyor", read=1, write=1, create=1, submit=1)
    
    # 3. Claims Officer
    add_custom_permission("Claim Survey", "Claims Officer", read=1, write=1, submit=1)
    add_custom_permission("Claim Verification", "Claims Officer", read=1, write=1, create=1, submit=1)
    
    # 4. Insurance Underwriter
    add_custom_permission("Insurance Proposal", "Insurance Underwriter", read=1, write=1, submit=1)
    # Give Underwriter permission level 1 access too
    add_custom_permission("Insurance Proposal", "Insurance Underwriter", permlevel=1, read=1, write=1)

    # 5. Ensure the verification agent role exists if used in JSON
    if not frappe.db.exists("Role", "Claim Verification Agent"):
        frappe.get_doc({"doctype": "Role", "role_name": "Claim Verification Agent", "desk_access": 1}).insert(ignore_permissions=True)
    
    # Assign verification role to claims officer user
    claims_user = "claims@insurance.com"
    if frappe.db.exists("User", claims_user):
        user = frappe.get_doc("User", claims_user)
        if not any(r.role == "Claim Verification Agent" for r in user.roles):
            user.append("roles", {"role": "Claim Verification Agent"})
            user.save(ignore_permissions=True)

    frappe.db.commit()
    frappe.clear_cache()
    print("\n--- Permissions Fixed ---")

if __name__ == "__main__":
    fix_all_permissions()
