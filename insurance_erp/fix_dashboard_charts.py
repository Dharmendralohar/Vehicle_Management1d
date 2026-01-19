import frappe
from frappe import _

def create_dashboard_chart(data):
    if frappe.db.exists("Dashboard Chart", data["name"]):
        frappe.delete_doc("Dashboard Chart", data["name"], force=True)
        print(f"Deleted existing Dashboard Chart: {data['name']}")

    doc = frappe.new_doc("Dashboard Chart")
    doc.update(data)
    doc.insert(ignore_permissions=True)
    print(f"Created Dashboard Chart: {data['name']}")

def main():
    charts = [
        {
            "name": "Active Policies by Plan",
            "chart_name": "Active Policies by Plan",
            "chart_type": "Group By",
            "type": "Donut",
            "report_name": "Active Policies",
            "group_by_based_on": "insurance_plan",
            "group_by_type": "Count",
            "document_type": "Insurance Policy",
            "filters_json": '[]',
            "module": "Insurance Erp",
            "is_public": 1,
            "is_standard": 1
        },
        {
            "name": "Claims by Status",
            "chart_name": "Claims by Status",
            "chart_type": "Group By",
            "type": "Pie",
            "document_type": "Insurance Claim",
            "group_by_based_on": "claim_status",
            "group_by_type": "Count",
            "filters_json": '[]',
            "module": "Insurance Erp",
            "is_public": 1,
            "is_standard": 1
        }
    ]

    for chart in charts:
        try:
            create_dashboard_chart(chart)
        except Exception as e:
            print(f"Error creating chart {chart['name']}: {e}")

    frappe.db.commit()

if __name__ == "__main__":
    main()

