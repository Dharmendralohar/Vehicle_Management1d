import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup_all_custom_fields():
    custom_fields = {
        "Sales Order": [
            {
                "fieldname": "insurance_section",
                "fieldtype": "Section Break",
                "label": "Insurance Proposal",
                "insert_after": "title"
            },
            {
                "fieldname": "is_insurance_proposal",
                "fieldtype": "Check",
                "label": "Is Insurance Proposal",
                "default": 0,
                "insert_after": "insurance_section"
            },
            {
                "fieldname": "insurance_plan",
                "fieldtype": "Link",
                "label": "Insurance Plan",
                "options": "Insurance Plan",
                "insert_after": "is_insurance_proposal",
                "depends_on": "eval:doc.is_insurance_proposal==1"
            },
            {
                "fieldname": "vehicle",
                "fieldtype": "Link",
                "label": "Vehicle",
                "options": "Vehicle",
                "insert_after": "insurance_plan",
                "depends_on": "eval:doc.is_insurance_proposal==1"
            },
            {
                "fieldname": "idv",
                "fieldtype": "Currency",
                "label": "Declared Value (IDV)",
                "insert_after": "vehicle",
                "depends_on": "eval:doc.is_insurance_proposal==1"
            },
            {
                "fieldname": "ncb_percent",
                "fieldtype": "Select",
                "label": "NCB %",
                "options": "0\n20\n25\n35\n45\n50",
                "default": "0",
                "insert_after": "idv",
                "depends_on": "eval:doc.is_insurance_proposal==1"
            },
            {
                "fieldname": "policy_duration_from",
                "fieldtype": "Date",
                "label": "Policy Start Date",
                "insert_after": "ncb_percent",
                "depends_on": "eval:doc.is_insurance_proposal==1"
            },
            {
                "fieldname": "policy_duration_to",
                "fieldtype": "Date",
                "label": "Policy End Date",
                "insert_after": "policy_duration_from",
                "depends_on": "eval:doc.is_insurance_proposal==1"
            },
            {
                "fieldname": "proposal_addons",
                "fieldtype": "Table",
                "label": "Add-ons",
                "options": "Proposal Addon",
                "insert_after": "policy_duration_to",
                "depends_on": "eval:doc.is_insurance_proposal==1"
            },
            {
                "fieldname": "premium_breakdown_section",
                "fieldtype": "Section Break",
                "label": "Premium Breakdown",
                "insert_after": "proposal_addons",
                "depends_on": "eval:doc.is_insurance_proposal==1"
            },
            {
                "fieldname": "od_premium",
                "fieldtype": "Currency",
                "label": "OD Premium (Net)",
                "read_only": 1,
                "insert_after": "premium_breakdown_section"
            },
            {
                "fieldname": "tp_premium",
                "fieldtype": "Currency",
                "label": "TP Premium",
                "read_only": 1,
                "insert_after": "od_premium"
            },
            {
                "fieldname": "addon_premium",
                "fieldtype": "Currency",
                "label": "Add-on Premium",
                "read_only": 1,
                "insert_after": "tp_premium"
            },
            {
                "fieldname": "total_net_premium",
                "fieldtype": "Currency",
                "label": "Total Net Premium",
                "read_only": 1,
                "insert_after": "addon_premium"
            },
            {
                "fieldname": "total_gst",
                "fieldtype": "Currency",
                "label": "Total GST",
                "read_only": 1,
                "insert_after": "total_net_premium"
            },
            {
                "fieldname": "grand_total_premium",
                "fieldtype": "Currency",
                "label": "Grand Total Premium",
                "read_only": 1,
                "insert_after": "total_gst"
            }
        ],
        "Sales Invoice": [
            {
                "fieldname": "insurance_section",
                "fieldtype": "Section Break",
                "label": "Insurance Policy",
                "insert_after": "title"
            },
            {
                "fieldname": "is_insurance_policy",
                "fieldtype": "Check",
                "label": "Is Insurance Policy",
                "default": 0,
                "insert_after": "insurance_section"
            },
            {
                "fieldname": "policy_number",
                "fieldtype": "Data",
                "label": "Policy Number",
                "read_only": 1,
                "insert_after": "is_insurance_policy",
                "depends_on": "eval:doc.is_insurance_policy==1"
            },
            {
                "fieldname": "policy_status",
                "fieldtype": "Select",
                "label": "Policy Status",
                "options": "Draft\nPending Payment\nActive\nLapsed\nCancelled\nExpired",
                "default": "Draft",
                "insert_after": "policy_number",
                "depends_on": "eval:doc.is_insurance_policy==1"
            },
            {
                "fieldname": "vehicle",
                "fieldtype": "Link",
                "label": "Vehicle",
                "options": "Vehicle",
                "insert_after": "policy_status",
                "depends_on": "eval:doc.is_insurance_policy==1"
            },
            {
                "fieldname": "idv",
                "fieldtype": "Currency",
                "label": "Declared Value (IDV)",
                "read_only": 1,
                "insert_after": "vehicle",
                "depends_on": "eval:doc.is_insurance_policy==1"
            },
            {
                "fieldname": "policy_start_date",
                "fieldtype": "Date",
                "label": "Policy Start Date",
                "insert_after": "idv",
                "depends_on": "eval:doc.is_insurance_policy==1"
            },
            {
                "fieldname": "policy_end_date",
                "fieldtype": "Date",
                "label": "Policy End Date",
                "insert_after": "policy_start_date",
                "depends_on": "eval:doc.is_insurance_policy==1"
            },
            {
                "fieldname": "coverage_snapshot",
                "fieldtype": "Table",
                "label": "Coverage Snapshot",
                "options": "Policy Coverage Snapshot",
                "insert_after": "policy_end_date",
                "depends_on": "eval:doc.is_insurance_policy==1"
            }
        ]
    }
    
    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
