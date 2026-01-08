import frappe
import json

def dump_workflow():
    wf_name = "Insurance Claim Workflow"
    if not frappe.db.exists("Workflow", wf_name):
        print(f"Workflow {wf_name} not found.")
        return
        
    wf = frappe.get_doc("Workflow", wf_name)
    print("--- States ---")
    for s in wf.states:
        print(f"State: {s.state}, DocStatus: {s.doc_status}")
        
    print("\n--- Transitions ---")
    for t in wf.transitions:
        print(f"Action: {t.action}, From: {t.state}, To: {t.next_state}")

    doc_name = "CLM-2026-00010"
    if frappe.db.exists("Insurance Claim", doc_name):
        doc = frappe.get_doc("Insurance Claim", doc_name)
        print(f"\n--- Document: {doc_name} ---")
        print(f"DocStatus: {doc.docstatus}")
        print(f"Workflow State: {doc.workflow_state}")

if __name__ == "__main__":
    dump_workflow()
