import frappe
import requests
import json

@frappe.whitelist()
def fetch_vehicle_rc(reg_no):
    """
    Fetches vehicle RC details from Cashfree API.
    """
    # 1. Get Settings
    settings = frappe.get_single("Insurance System Settings")
    if not settings.enable_vehicle_rc_verification:
        frappe.throw("Vehicle RC Verification is disabled in 'Insurance System Settings'.")
        
    if settings.rc_verification_provider != "Cashfree":
        frappe.throw(f"Provider '{settings.rc_verification_provider}' not implemented in this script.")

    if not settings.cashfree_client_id or not settings.cashfree_client_secret:
        frappe.throw("Cashfree API Credentials not configured in 'Insurance System Settings'.")

    # 2. Determine URL
    base_url = "https://sandbox.cashfree.com" if settings.cashfree_environment == "Sandbox" else "https://api.cashfree.com"
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
        timeout = settings.rc_api_timeout or 30
        response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
        
        # Log response for debugging/audit
        # frappe.log_error(message=response.text, title=f"Cashfree RC RAW Response: {reg_no}")
        
        if response.status_code != 200:
            data = response.json()
            error_msg = data.get("message", "Unknown error from Cashfree")
            frappe.log_error(message=f"Status: {response.status_code}, Body: {response.text}", title=f"Cashfree RC Error: {reg_no}")
            return {"status": "ERROR", "message": error_msg, "raw_response": response.text}

        data = response.json()
        return {"status": "SUCCESS", "data": data, "raw_response": response.text}

    except requests.exceptions.Timeout:
        frappe.log_error(message="API Request Timed Out", title=f"Cashfree RC Timeout: {reg_no}")
        return {"status": "TIMEOUT", "message": "API Request Timed Out"}

    except requests.exceptions.RequestException as e:
        frappe.log_error(message=str(e), title=f"Cashfree RC Connection Error: {reg_no}")
        return {"status": "ERROR", "message": str(e)}

    except Exception as e:
        frappe.log_error(message=str(e), title=f"Cashfree RC Code Error")
        return {"status": "ERROR", "message": f"An unexpected error occurred: {str(e)}"}
