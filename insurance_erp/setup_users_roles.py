import frappe
from frappe.utils import random_string

def setup_insurance_roles_and_users():
    print("Setting up Insurance Roles and Users...")
    
    roles = [
        "Insurance Agent",
        "Insurance Underwriter",
        "Claims Officer",
        "Surveyor"
    ]
    
    # 1. Create Roles
    for role_name in roles:
        if not frappe.db.exists("Role", role_name):
            print(f"Creating Role: {role_name}")
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1
            })
            role.insert(ignore_permissions=True)
    
    # 2. Define Users to Create
    users_data = [
        {"email": "agent@insurance.com", "first_name": "Insurance", "last_name": "Agent", "role": "Insurance Agent"},
        {"email": "underwriter@insurance.com", "first_name": "Insurance", "last_name": "Underwriter", "role": "Insurance Underwriter"},
        {"email": "claims@insurance.com", "first_name": "Claims", "last_name": "Officer", "role": "Claims Officer"},
        {"email": "surveyor@insurance.com", "first_name": "Internal", "last_name": "Surveyor", "role": "Surveyor"},
    ]
    
    for user_info in users_data:
        email = user_info["email"]
        if not frappe.db.exists("User", email):
            print(f"Creating User: {email}")
            user = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": user_info["first_name"],
                "last_name": user_info["last_name"],
                "send_welcome_email": 0,
                "roles": [
                    {"role": "Desk User"},
                    {"role": user_info["role"]}
                ]
            })
            # Set a default password
            user.insert(ignore_permissions=True)
            from frappe.utils.password import update_password
            update_password(user.name, "password123")
        else:
            print(f"User {email} already exists, ensuring role assignment...")
            user = frappe.get_doc("User", email)
            has_role = any(r.role == user_info["role"] for r in user.roles)
            if not has_role:
                user.append("roles", {"role": user_info["role"]})
                user.save(ignore_permissions=True)

    frappe.db.commit()
    print("\n--- Setup Complete ---")
    print("Default password for all new users: password123")
    for u in users_data:
        print(f"User: {u['email']} | Role: {u['role']}")

if __name__ == "__main__":
    setup_insurance_roles_and_users()
