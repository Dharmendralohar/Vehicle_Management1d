// Copyright (c) 2026, Insurance Solutions Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Insurance Proposal', {
    refresh: function (frm) {
        if (frm.doc.status === 'Approved' && frm.doc.docstatus === 1) {

            // Check for submitted payment linked to this proposal
            frappe.db.get_value('Payment Entry', { 'reference_no': frm.doc.name, 'docstatus': 1 }, 'name')
                .then(r => {
                    if (r && r.message && r.message.name) {
                        // Payment Done -> Show Convert to Policy
                        frm.add_custom_button(__('Convert to Policy'), function () {
                            frappe.call({
                                method: "insurance_erp.insurance_erp.doctype.insurance_proposal.insurance_proposal.create_policy_from_proposal",
                                args: {
                                    proposal_name: frm.doc.name
                                },
                                freeze: true,
                                callback: function (r) {
                                    if (r.message) {
                                        frappe.set_route('Form', 'Insurance Policy', r.message);
                                    }
                                }
                            });
                        }, __('Actions')).addClass("btn-primary");
                    } else {
                        // Payment Not Done -> Show Record Payment
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
                        }, __('Actions')).addClass("btn-primary");
                    }
                });
        }
    }
});
