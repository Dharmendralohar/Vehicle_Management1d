import frappe
import json

def check_perms():
    doctype = "Vehicle"
    print(f"--- Permissions for {doctype} ---")
    
    # Check DocType.json perms (Standard)
    meta = frappe.get_meta(doctype)
    print("\n[Standard Permissions (DocType.json)]")
    for p in meta.permissions:
        print(f"Role: {p.role}, Read: {p.read}, Write: {p.write}, Create: {p.create}")
        
    # Check Custom DocPerm (Overrides)
    custom_perms = frappe.get_all("Custom DocPerm", filters={"parent": doctype}, fields=["*"])
    print(f"\n[Custom Permissions (Overrides) - Found {len(custom_perms)}]")
    for p in custom_perms:
        print(f"Role: {p.role}, Read: {p.read}, Write: {p.write}, Create: {p.create}, Delete: {p.delete}")

    if custom_perms:
        print("\nNOTE: Custom permissions are ACTIVE. Standard permissions are being ignored.")
    else:
        print("\nNOTE: No custom permissions. Standard permissions should be in effect.")

if __name__ == "__main__":
    check_perms()
