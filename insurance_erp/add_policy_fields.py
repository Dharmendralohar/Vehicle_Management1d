import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_policy_fields():
    custom_fields = {
        "Insurance Policy": [
            {
                "fieldname": "nominee_section",
                "fieldtype": "Section Break",
                "label": "Nominee Details"
            },
            {
                "fieldname": "nominee",
                "fieldtype": "Data",
                "label": "Nominee Name"
            },
            {
                "fieldname": "nominee_relationship",
                "fieldtype": "Data",
                "label": "Nominee Relationship"
            }
        ]
    }
    create_custom_fields(custom_fields)
    print("Added custom fields to Insurance Policy")

if __name__ == "__main__":
    add_policy_fields()
