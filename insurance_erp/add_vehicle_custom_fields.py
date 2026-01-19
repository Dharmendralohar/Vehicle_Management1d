import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_vehicle_custom_fields():
    custom_fields = {
        "Vehicle": [
            {
                "fieldname": "custom_vehicle_details_section",
                "fieldtype": "Section Break",
                "label": "Insurance Details"
            },
            {
                "fieldname": "custom_rto_location",
                "fieldtype": "Data",
                "label": "RTO Location"
            },
            {
                "fieldname": "custom_vehicle_category",
                "fieldtype": "Select",
                "options": "Private\nCommercial",
                "label": "Vehicle Category",
                "default": "Private"
            },
            {
                "fieldname": "custom_body_type",
                "fieldtype": "Data",
                "label": "Body Type"
            },
            {
                "fieldname": "custom_engine_cc",
                "fieldtype": "Int",
                "label": "Engine CC"
            },
            {
                "fieldname": "custom_manufacturing_year",
                "fieldtype": "Int",
                "label": "Manufacturing Year"
            },
            {
                "fieldname": "custom_seating_capacity",
                "fieldtype": "Int",
                "label": "Seating Capacity"
            },
            {
                "fieldname": "custom_engine_number",
                "fieldtype": "Data",
                "label": "Engine Number"
            },
            {
                "fieldname": "custom_vehicle_idv",
                "fieldtype": "Currency",
                "label": "Insured Declared Value (IDV)"
            }
            # chassis_no and fuel_type are assumed standard, but adding if missing is safer? 
            # Gap analysis said chassis_no exists. fuel_type usually exists.
        ]
    }
    
    # Check for chassis_no and fuel_type
    meta = frappe.get_meta("Vehicle")
    if not meta.get_field("chassis_no"):
        custom_fields["Vehicle"].append({
            "fieldname": "chassis_no",
            "fieldtype": "Data",
            "label": "Chassis Number"
        })
    if not meta.get_field("fuel_type"):
        custom_fields["Vehicle"].append({
             "fieldname": "fuel_type",
             "fieldtype": "Select",
             "options": "Petrol\nDiesel\nElectric\nCNG",
             "label": "Fuel Type"
        })

    create_custom_fields(custom_fields)
    print("Vehicle Custom Fields added.")

if __name__ == "__main__":
    add_vehicle_custom_fields()
