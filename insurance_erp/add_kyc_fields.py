import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_kyc_fields():
    custom_fields = {
        "Customer": [
            {
                "fieldname": "kyc_section",
                "fieldtype": "Section Break",
                "label": "KYC Details",
                "insert_after": "mobile_no"
            },
            {
                "fieldname": "custom_pan",
                "fieldtype": "Data",
                "label": "PAN Number",
                "insert_after": "kyc_section"
            },
            {
                "fieldname": "custom_aadhaar",
                "fieldtype": "Data",
                "label": "Aadhaar Number",
                "insert_after": "custom_pan",
                "permlevel": 1 # Restricted
            },
            {
                "fieldname": "custom_dob",
                "fieldtype": "Date",
                "label": "Date of Birth",
                "insert_after": "custom_aadhaar"
            },
            {
                "fieldname": "custom_nominee",
                "fieldtype": "Data",
                "label": "Nominee Name",
                "insert_after": "custom_dob"
            }
        ]
    }

    create_custom_fields(custom_fields)
    print("KYC Fields added to Customer.")

if __name__ == "__main__":
    add_kyc_fields()
