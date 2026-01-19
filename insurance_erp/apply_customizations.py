import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def apply_customizations():
    # 1. Add Custom Fields to standard DocTypes
    custom_fields = {
        "Vehicle": [
            {"fieldname": "custom_rto_location", "label": "RTO Location", "fieldtype": "Data", "reqd": 1, "insert_after": "license_plate"},
            {"fieldname": "custom_vehicle_category", "label": "Vehicle Category", "fieldtype": "Select", "options": "Private Car\nTwo Wheeler\nCommercial Vehicle", "reqd": 1, "insert_after": "custom_rto_location"},
            {"fieldname": "custom_body_type", "label": "Body Type", "fieldtype": "Data", "reqd": 1, "insert_after": "model"},
            {"fieldname": "custom_engine_cc", "label": "Engine CC", "fieldtype": "Int", "reqd": 1, "insert_after": "custom_body_type"},
            {"fieldname": "custom_manufacturing_year", "label": "Manufacturing Year", "fieldtype": "Int", "reqd": 1, "insert_after": "custom_engine_cc"},
            {"fieldname": "custom_seating_capacity", "label": "Seating Capacity", "fieldtype": "Int", "reqd": 1, "insert_after": "custom_manufacturing_year"},
            {"fieldname": "custom_engine_number", "label": "Engine Number", "fieldtype": "Data", "reqd": 1, "insert_after": "chassis_no"},
            {"fieldname": "custom_vehicle_idv", "label": "Insured Declared Value (IDV)", "fieldtype": "Currency", "reqd": 1, "insert_after": "vehicle_value"}
        ],
        "Customer": [
            {"fieldname": "custom_mobile_verified", "label": "Mobile Verified", "fieldtype": "Check", "insert_after": "mobile_no"}
        ]
    }
    
    create_custom_fields(custom_fields, ignore_validate=True)
    
    # 2. Update Property Setters for mandatory fields
    property_setters = [
        {"doc_type": "Vehicle", "field_name": "license_plate", "property": "reqd", "value": "1"},
        {"doc_type": "Vehicle", "field_name": "make", "property": "reqd", "value": "1"},
        {"doc_type": "Vehicle", "field_name": "model", "property": "reqd", "value": "1"},
        {"doc_type": "Vehicle", "field_name": "fuel_type", "property": "reqd", "value": "1"},
        {"doc_type": "Vehicle", "field_name": "chassis_no", "property": "reqd", "value": "1"},
        {"doc_type": "Vehicle", "field_name": "vehicle_value", "property": "reqd", "value": "1"},
        {"doc_type": "Address", "field_name": "address_line1", "property": "reqd", "value": "1"},
        {"doc_type": "Address", "field_name": "city", "property": "reqd", "value": "1"},
        {"doc_type": "Address", "field_name": "pincode", "property": "reqd", "value": "1"},
        {"doc_type": "Customer", "field_name": "mobile_no", "property": "reqd", "value": "1"},
        {"doc_type": "Customer", "field_name": "email_id", "property": "reqd", "value": "1"}
    ]
    
    for ps in property_setters:
        if not frappe.db.exists("Property Setter", {"doc_type": ps["doc_type"], "field_name": ps["field_name"], "property": ps["property"]}):
            frappe.get_doc({
                "doctype": "Property Setter",
                "doctype_or_field": "DocField",
                "doc_type": ps["doc_type"],
                "field_name": ps["field_name"],
                "property": ps["property"],
                "value": ps["value"],
                "property_type": "Check"
            }).insert(ignore_permissions=True)

if __name__ == "__main__":
    apply_customizations()
    frappe.db.commit()
    print("Customizations applied successfully.")
