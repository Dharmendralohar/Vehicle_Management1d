// Copyright (c) 2026, Insurance Solutions Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Insurance Proposal', {
    refresh: function (frm) {
        if (frm.doc.status === 'Approved' && frm.doc.docstatus === 1) {

            // Record Payment Button
            frm.add_custom_button(__('Record Payment'), function () {
                frappe.call({
                    method: "insurance_erp.insurance_erp.doctype.insurance_proposal.insurance_proposal.create_proposal_payment_entry",
                    args: { proposal_name: frm.doc.name },
                    callback: function (r) {
                        if (r.message) {
                            frappe.set_route("Form", "Payment Entry", r.message);
                        }
                    }
                });
            }, __('Actions'));

            // Convert to Policy Button
            frm.add_custom_button(__('Convert to Policy'), function () {
                frappe.call({
                    method: "insurance_erp.insurance_erp.doctype.insurance_proposal.insurance_proposal.create_policy_from_proposal",
                    args: {
                        proposal_name: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            frappe.set_route('Form', 'Insurance Policy', r.message);
                        }
                    }
                });
            }, __('Actions'));
        }
    }
});
