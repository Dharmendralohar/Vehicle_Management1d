import frappe

def fix_policy_payment():
    policy_name = "POL-2026-00007"
    if frappe.db.exists("Insurance Policy", policy_name):
        policy = frappe.get_doc("Insurance Policy", policy_name)
        policy.db_set("premium_paid", policy.premium_amount)
        policy.db_set("outstanding_amount", 0)
        policy.db_set("status", "Active")
        frappe.db.commit()
        print(f"Policy {policy_name} updated to Active.")
    else:
        print(f"Policy {policy_name} not found.")

if __name__ == "__main__":
    fix_policy_payment()
