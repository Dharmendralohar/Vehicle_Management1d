frappe.ui.form.on('Insurance Policy', {
    refresh: function (frm) {
        // Clear existing custom buttons
        frm.clear_custom_buttons();

        // 1. Quick Payment Button (Server-side to avoid JS crashes)
        if (frm.doc.outstanding_amount > 0) {
            frm.add_custom_button(__('Record Payment'), function () {
                let d = new frappe.ui.Dialog({
                    title: __('Record Premium Payment'),
                    fields: [
                        {
                            label: __('Mode of Payment'),
                            fieldname: 'mode_of_payment',
                            fieldtype: 'Link',
                            options: 'Mode of Payment',
                            reqd: 1,
                            on_change: function () {
                                let mop = this.get_value();
                                if (mop) {
                                    frappe.call({
                                        method: 'frappe.client.get_value',
                                        args: {
                                            doctype: 'Mode of Payment Account',
                                            filters: { parent: mop, company: frm.doc.company || frappe.defaults.get_default('company') },
                                            fieldname: 'default_account'
                                        },
                                        callback: function (r) {
                                            if (r.message) {
                                                d.set_value('paid_to', r.message.default_account);
                                            }
                                        }
                                    });
                                }
                            }
                        },
                        {
                            label: __('Paid To Account'),
                            fieldname: 'paid_to',
                            fieldtype: 'Link',
                            options: 'Account',
                            description: __('Bank or Cash account'),
                            reqd: 1
                        },
                        {
                            label: __('Amount'),
                            fieldname: 'amount',
                            fieldtype: 'Currency',
                            default: frm.doc.outstanding_amount,
                            reqd: 1
                        },
                        {
                            label: __('Reference No'),
                            fieldname: 'reference_no',
                            fieldtype: 'Data',
                            default: frm.doc.name,
                            description: __('Check/Draft or Internal Ref No')
                        },
                        {
                            label: __('Reference Date'),
                            fieldname: 'reference_date',
                            fieldtype: 'Date',
                            default: frappe.datetime.nowdate()
                        }
                    ],
                    primary_action_label: __('Confirm & Submit Payment'),
                    primary_action(values) {
                        frappe.confirm(__('Submit Payment Entry for {0}?', [format_currency(values.amount, frm.doc.currency)]), function () {
                            d.get_primary_btn().prop('disabled', true);
                            frappe.call({
                                method: 'insurance_erp.events.create_payment_for_policy',
                                args: {
                                    policy_name: frm.doc.name,
                                    mode_of_payment: values.mode_of_payment,
                                    paid_to: values.paid_to,
                                    amount: values.amount,
                                    reference_no: values.reference_no,
                                    reference_date: values.reference_date
                                },
                                callback: function (r) {
                                    if (r.message) {
                                        frappe.show_alert({ message: __('Payment Recorded Successfully'), indicator: 'green' });
                                        frm.reload_doc();
                                        d.hide();
                                    }
                                },
                                always: function () {
                                    d.get_primary_btn().prop('disabled', false);
                                }
                            });
                        });
                    }
                });
                d.show();
            }, __('Actions')).css({ 'background-color': '#28a745', 'color': 'white' });

            // Fallback option removed if it causes confusion, or merged?
            // Let's keep it but make it clear it's manual.
            frm.add_custom_button(__('Manual Payment Entry'), function () {
                frappe.set_route('List', 'Payment Entry', { 'party': frm.doc.customer });
                frappe.show_alert(__('Please create a new Payment Entry and manually select this Policy in the references table.'));
            }, __('Actions'));
        }

        if (frm.doc.docstatus === 1 || frm.doc.status === 'Active' || frm.doc.status === 'Expired') {
            // 2. Create Claim Button
            if (frm.doc.status !== 'Cancelled') {
                frm.add_custom_button(__('Create Claim'), function () {
                    frappe.new_doc('Insurance Claim', {
                        policy: frm.doc.name,
                        customer: frm.doc.customer,
                        vehicle: frm.doc.vehicle
                    });
                }, __('Actions'));
            }

            // 3. Cancel Policy Button
            if (frm.doc.status !== 'Cancelled' && frm.doc.status !== 'Expired') {
                frm.add_custom_button(__('Cancel Policy'), function () {
                    frappe.confirm(__('Are you sure you want to cancel this policy?'), function () {
                        frappe.db.set_value('Insurance Policy', frm.doc.name, 'status', 'Cancelled')
                            .then(r => {
                                frm.reload_doc();
                                frappe.show_alert({ message: __('Policy cancelled'), indicator: 'red' });
                            });
                    });
                }, __('Actions'));
            }
        }
    }
});
