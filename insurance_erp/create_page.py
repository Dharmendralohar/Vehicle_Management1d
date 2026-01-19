import frappe
import os

def create_page():
    page_name = "all-policies"
    if not frappe.db.exists("Page", page_name):
        doc = frappe.new_doc("Page")
        doc.page_name = page_name
        doc.title = "All Policies"
        doc.module = "Insurance Erp"
        doc.standard = "Yes"
        doc.public = 1
        doc.insert(ignore_permissions=True)
        print(f"Created Page: {page_name}")
    else:
        print(f"Page {page_name} already exists.")

if __name__ == "__main__":
    create_page()
