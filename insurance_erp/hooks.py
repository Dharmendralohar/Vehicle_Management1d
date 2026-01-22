import frappe

app_name = "insurance_erp"
app_title = "Insurance Erp"
app_publisher = "Insurance Solutions Inc"
app_description = "Vehicle Insurance Policy Management System"
app_email = "admin@example.com"
app_license = "mit"

# Document Events
doc_events = {
    "Payment Entry": {
        "on_submit": "insurance_erp.events.handle_payment_entry_submission"
    },
    "Journal Entry": {
        "validate": "insurance_erp.events.validate_journal_entry",
        "on_submit": "insurance_erp.events.handle_journal_entry_submission"
    },
    "Sales Order": {
        "validate": "insurance_erp.events.validate_sales_order"
    },
    "Sales Invoice": {
        "before_insert": "insurance_erp.events.before_insert_sales_invoice"
    }
}
# Scheduled Tasks
scheduler_events = {
	"daily": [
		"insurance_erp.insurance_erp.doctype.policy_renewal.policy_renewal.check_for_renewals"
	]
}
