import frappe
import requests
import json

@frappe.whitelist()
def fetch_vehicle_rc(reg_no):
    """
    Fetches vehicle RC details from Cashfree API.
    """
    # 1. Get Settings
    settings = frappe.get_single("Insurance Settings")
    if not settings.cashfree_client_id or not settings.cashfree_client_secret:
        frappe.throw("Cashfree API Credentials not configured in 'Insurance Settings'.")

    # 2. Determine URL
    # Using Cashfree Verification API Standard URLs
    # Sandbox: https://sandbox.cashfree.com/verification/vehicle-rc
    # Production: https://api.cashfree.com/verification/vehicle-rc
    base_url = "https://sandbox.cashfree.com" if settings.cashfree_env == "Sandbox" else "https://api.cashfree.com"
    endpoint = f"{base_url}/verification/vehicle-rc"

    # 3. Prepare Request
    headers = {
        "x-client-id": settings.cashfree_client_id,
        "x-client-secret": settings.get_password("cashfree_client_secret"),
        "Content-Type": "application/json"
    }
    payload = {
        "vehicle_number": reg_no
    }

    try:
        # 4. Call API
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 5. Log for audit if needed (optional)
        # frappe.log_error(message=json.dumps(data), title=f"Cashfree RC Response: {reg_no}")

        return data

    except requests.exceptions.RequestException as e:
        frappe.log_error(message=str(e), title=f"Cashfree RC Error: {reg_no}")
        frappe.throw(f"Failed to fetch vehicle details from Cashfree: {str(e)}")

    except Exception as e:
        frappe.log_error(message=str(e), title=f"Cashfree RC Unknown Error")
        frappe.throw(f"An unexpected error occurred: {str(e)}")
