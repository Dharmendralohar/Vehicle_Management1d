import frappe
from frappe.model.document import Document
from frappe import _

class PolicyEndorsement(Document):
    def validate(self):
        self.validate_policy_status()
        self.calculate_premium_diff()

    def validate_policy_status(self):
        if self.insurance_policy:
            status = frappe.db.get_value("Insurance Policy", self.insurance_policy, "status")
            if status != "Active":
                frappe.throw(_("Endorsements can only be created for Active policies."))

    def calculate_premium_diff(self):
        # Placeholder logic: for now manual entry of additional premium
        pass

    def on_submit(self):
        # Update the linked policy
        policy = frappe.get_doc("Insurance Policy", self.insurance_policy)
        
        if self.new_nominee:
            policy.db_set("nominee", self.new_nominee)
        
        # If premium changed, log it or update
        # For this prototype, we just log the endorsement in a child table on Policy if needed
        # or relying on the 'links' 
        
        policy.add_comment("Info", f"Endorsed via {self.name}")
