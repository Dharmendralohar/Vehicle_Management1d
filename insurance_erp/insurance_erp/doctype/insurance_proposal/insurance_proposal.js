frappe.ui.form.on('Insurance Proposal', {
    refresh: function (frm) {
        // Clear existing custom buttons
        frm.clear_custom_buttons();

        // Button logic based on status field
        if (frm.doc.status !== 'Approved' && frm.doc.status !== 'Rejected') {

            // 1. Submit for Review button
            if (frm.doc.status === 'Draft' || frm.doc.status === 'Submitted') {
                frm.add_custom_button(__('Submit for Review'), function () {
                    frappe.db.set_value('Insurance Proposal', frm.doc.name, 'status', 'Under Review')
                        .then(r => {
                            frm.reload_doc();
                            frappe.show_alert({ message: __('Proposal status updated to Under Review'), indicator: 'blue' });
                        });
                }, __('Actions'));
            }

            // 2. Approve/Reject buttons
            if (frm.doc.status === 'Under Review') {
                frm.add_custom_button(__('Approve'), function () {
                    frappe.confirm(__('Are you sure you want to approve this proposal?'), function () {
                        frappe.db.set_value('Insurance Proposal', frm.doc.name, 'status', 'Approved')
                            .then(r => {
                                frm.reload_doc();
                                frappe.show_alert({ message: __('Proposal approved'), indicator: 'green' });
                            });
                    });
                }, __('Actions')).css({ 'background-color': '#28a745', 'color': 'white' });

                frm.add_custom_button(__('Reject'), function () {
                    frappe.prompt({
                        label: 'Rejection Reason',
                        fieldname: 'reason',
                        fieldtype: 'Small Text',
                        reqd: 1
                    }, function (values) {
                        frappe.db.set_value('Insurance Proposal', frm.doc.name, {
                            'status': 'Rejected',
                            'risk_assessment_notes': (frm.doc.risk_assessment_notes || '') + '\n\nRejection Reason: ' + values.reason
                        }).then(r => {
                            frm.reload_doc();
                            frappe.show_alert({ message: __('Proposal rejected'), indicator: 'red' });
                        });
                    }, __('Reject Proposal'), __('Reject'));
                }, __('Actions')).css({ 'background-color': '#dc3545', 'color': 'white' });
            }
        }

        // 3. Create Policy button (only for Approved)
        if (frm.doc.status === 'Approved') {
            frm.add_custom_button(__('Create Policy'), function () {
                frappe.call({
                    method: 'insurance_erp.insurance_erp.doctype.insurance_proposal.insurance_proposal.create_policy_from_proposal',
                    args: {
                        proposal_name: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            frappe.set_route('Form', 'Insurance Policy', r.message);
                        }
                    }
                });
            }, __('Actions')).css({ 'background-color': '#007bff', 'color': 'white' });
        }
    },

    // Auto-fetch IDV when vehicle changes
    vehicle: function (frm) {
        if (frm.doc.vehicle) {
            frappe.db.get_value('Vehicle', frm.doc.vehicle, 'current_idv', (r) => {
                if (r && r.current_idv) {
                    frm.set_value('vehicle_idv', r.current_idv);
                }
            });
        }
    },

    // Auto-calculate policy end date
    policy_duration_from: function (frm) {
        if (frm.doc.policy_duration_from) {
            let end_date = frappe.datetime.add_months(frm.doc.policy_duration_from, 12);
            // Subtract 1 day for a perfect year (e.g. 01-Jan-2024 to 31-Dec-2024)
            end_date = frappe.datetime.add_days(end_date, -1);
            frm.set_value('policy_duration_to', end_date);
        }
    }
});
