// Copyright (c) 2026, Insurance Solutions Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Insurance Proposal', {
    refresh: function (frm) {
        if (frm.doc.status === 'Approved' && frm.doc.docstatus === 1) {
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
