import frappe

def create_dashboard_and_workspace():
    print("Setting up Insurance Dashboard and Workspace...")
    
    # 1. Create Number Cards
    cards = [
        {
            "name": "Total Active Policies",
            "label": "Total Active Policies",
            "document_type": "Insurance Policy",
            "function": "Count",
            "aggregate_function_based_on": "name",
            "filters_json": '[["Insurance Policy","status","=","Active"]]',
            "color": "Green"
        },
        {
            "name": "Total Claims Monthly",
            "label": "Total Claims (This Month)",
            "document_type": "Insurance Claim",
            "function": "Count",
            "aggregate_function_based_on": "name",
            "filters_json": '[["Insurance Claim","claim_registration_date",">","Month Start"]]',
            "color": "Red"
        },
        {
            "name": "Total Premium Collected",
            "label": "Total Premium Collected",
            "document_type": "Insurance Policy",
            "function": "Sum",
            "aggregate_function_based_on": "premium_paid",
            "color": "Blue"
        }
    ]
    
    for card_data in cards:
        if not frappe.db.exists("Number Card", card_data["name"]):
            print(f"Creating Number Card: {card_data['name']}")
            card = frappe.get_doc({
                "doctype": "Number Card",
                "module": "Insurance Erp",
                **card_data
            })
            card.insert(ignore_permissions=True)

    # 2. Create Dashboard Charts
    charts = [
        {
            "chart_name": "Claims by Status",
            "chart_type": "Count",
            "document_type": "Insurance Claim",
            "group_by_based_on": "status",
            "type": "Donut",
            "module": "Insurance Erp",
            "width": "Half"
        },
        {
            "chart_name": "Policy Expiry Trend",
            "chart_type": "Count",
            "document_type": "Insurance Policy",
            "group_by_based_on": "policy_end_date",
            "group_by_type": "Count",
            "type": "Line",
            "timeseries": 1,
            "timespan": "Last Year",
            "time_interval": "Month",
            "module": "Insurance Erp",
            "width": "Half"
        }
    ]
    
    for chart_data in charts:
        if not frappe.db.exists("Dashboard Chart", chart_data["chart_name"]):
            print(f"Creating Dashboard Chart: {chart_data['chart_name']}")
            chart = frappe.get_doc({
                "doctype": "Dashboard Chart",
                **chart_data
            })
            chart.insert(ignore_permissions=True)

    # 3. Create/Update Workspace
    workspace_name = "Insurance"
    if not frappe.db.exists("Workspace", workspace_name):
        print(f"Creating Workspace: {workspace_name}")
        workspace = frappe.get_doc({
            "doctype": "Workspace",
            "label": workspace_name,
            "title": workspace_name,
            "module": "Insurance Erp",
            "icon": "insurance",
            "public": 1,
            "content": "[]", # Blocks content
            "shortcuts": [
                {"label": "New Proposal", "link_to": "Insurance Proposal", "type": "DocType", "icon": "add"},
                {"label": "New Claim", "link_to": "Insurance Claim", "type": "DocType", "icon": "add"},
                {"label": "Active Policies", "link_to": "Insurance Policy", "type": "DocType", "icon": "list", "filters": '[["Insurance Policy","status","=","Active"]]'},
                {"label": "Pending Payments", "link_to": "Insurance Policy", "type": "DocType", "icon": "list", "filters": '[["Insurance Policy","status","=","Pending Payment"]]'}
            ],
            "charts": [
                {"chart_name": "Claims by Status", "width": "Half"},
                {"chart_name": "Policy Expiry Trend", "width": "Half"}
            ],
            "number_cards": [
                {"number_card_name": "Total Active Policies"},
                {"number_card_name": "Total Claims Monthly"},
                {"number_card_name": "Total Premium Collected"}
            ]
        })
        workspace.insert(ignore_permissions=True)
    else:
        print(f"Workspace {workspace_name} already exists. Consider manual update or script extension if needed.")

    frappe.db.commit()
    print("Dashboard and Workspace setup complete.")

if __name__ == "__main__":
    create_dashboard_and_workspace()
