import frappe
import json
from frappe import _

def create_number_card(data):
    if frappe.db.exists("Number Card", data["name"]):
        frappe.delete_doc("Number Card", data["name"], force=True)
    
    doc = frappe.new_doc("Number Card")
    doc.update(data)
    doc.insert(ignore_permissions=True)
    print(f"Created Number Card: {data['name']}")

def reset_workspace():
    workspace_name = "Insurance"
    
    # 1. Create Number Cards
    cards = [
        {
            "name": "Active Policies",
            "label": "Active Policies",
            "function": "Count",
            "document_type": "Insurance Policy",
            "filters_json": '[["Insurance Policy","status","=","Active",false]]',
            "is_public": 1,
            "is_standard": 1,
            "module": "Insurance Erp"
        },
        {
            "name": "Approved Claims",
            "label": "Approved Claims",
            "function": "Count",
            "document_type": "Insurance Claim",
            "filters_json": '[["Insurance Claim","claim_status","=","Approved",false]]',
            "is_public": 1,
            "is_standard": 1,
            "module": "Insurance Erp"
        }
    ]

    for card in cards:
        create_number_card(card)

    # 2. Define Workspace Content
    # Using flat list as validated previously.
    target_content = [
        {
            "type": "header",
            "data": {"text": f"Performance Overview", "col": 12}
        },
        {
            "type": "number_card", 
            "data": {"card_name": "Active Policies", "col": 4}
        },
        {
            "type": "number_card", 
            "data": {"card_name": "Approved Claims", "col": 4}
        },
        {
            "type": "shortcut",
            "data": {
                "shortcut_name": "New Proposal",
                "label": "New Proposal", 
                "type": "URL", 
                "link_to": "/app/insurance-proposal/new",
                "col": 4
            }
        },
        {
            "type": "shortcut",
            "data": {
                "shortcut_name": "All Policies",
                "label": "All Policies", 
                "type": "URL", 
                "link_to": "/app/all-policies",
                "col": 4
            }
        },
        {
            "type": "chart", 
            "data": {"chart_name": "Active Policies by Plan", "col": 12}
        },
        {
            "type": "chart", 
            "data": {"chart_name": "Claims by Status", "col": 12}
        },
        {
            "type": "card",
            "data": {
                "card_name": "Quick Links",
                "col": 12,
                "links": [
                    {"label": "Insurance Proposal", "link_to": "Insurance Proposal", "type": "DocType"},
                    {"label": "Insurance Policy", "link_to": "Insurance Policy", "type": "DocType"},
                    {"label": "Insurance Claim", "link_to": "Insurance Claim", "type": "DocType"},
                     {"label": "Vehicle", "link_to": "Vehicle", "type": "DocType"}
                ]
            }
        }
    ]

    # 3. Update Workspace
    if not frappe.db.exists("Workspace", workspace_name):
        print(f"Workspace {workspace_name} not found.")
        return

    ws = frappe.get_doc("Workspace", workspace_name)
    ws.content = json.dumps(target_content)
    
    # Also populate child tables for standard compliance (optional but good)
    # Clearing logic if needed, but 'content' usually overrides rendering.
    
    ws.save(ignore_permissions=True)
    print(f"Workspace {workspace_name} content updated with Cards and Shortcuts.")
