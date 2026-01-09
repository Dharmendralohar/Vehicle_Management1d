// Copyright (c) 2026, Insurance Solutions Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Insurance Claim', {
    refresh: function (frm) {
        if (frm.doc.claim_status === 'Approved' && !frm.doc.settlement_journal_entry) {
            frm.add_custom_button(__('Create Settlement JE'), function () {
                frappe.call({
                    method: "insurance_erp.insurance_erp.doctype.insurance_claim.insurance_claim.create_settlement_je",
                    args: {
                        claim_name: frm.doc.name
                    }
                });
            }, __('Actions'));
        }
    },

    policy: function (frm) {
        if (frm.doc.policy) {
            // Field fetching logic is already in the server-side before_insert/validate, 
            // but we can add immediate fetching for UX
            frappe.db.get_doc('Insurance Policy', frm.doc.policy).then(policy => {
                frm.set_value('customer', policy.customer);
                frm.set_value('vehicle', policy.vehicle);
                frm.set_value('policy_number', policy.policy_number);
                frm.set_value('insurance_plan', policy.insurance_plan);
            });
        }
    }
});
