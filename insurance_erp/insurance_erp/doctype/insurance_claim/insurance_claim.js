frappe.ui.form.on('Insurance Claim', {
    refresh: function (frm) {
        // Set query for policy to show only Active or Expired policies (claims can sometimes be backdated)
        frm.set_query('policy', function () {
            return {
                filters: [
                    ['Insurance Policy', 'status', 'in', ['Active', 'Expired']]
                ]
            };
        });

        // Dynamic Filtering for Coverage Type
        if (frm.doc.policy) {
            frm.trigger('set_coverage_filters');
        }
    },

    policy: function (frm) {
        if (frm.doc.policy) {
            // Trigger fetch from policy snapshot
            frappe.model.with_doc('Insurance Policy', frm.doc.policy, function () {
                let policy = frappe.get_doc('Insurance Policy', frm.doc.policy);

                // Customer and Vehicle are already fetched via fetch_from in JSON
                // But we need to handle Coverage Type options
                frm.trigger('set_coverage_filters');
            });
        }
    },

    set_coverage_filters: function (frm) {
        // Fetch coverage types from the policy snapshot and update the Select field
        frappe.call({
            method: 'frappe.client.get_value',
            args: {
                doctype: 'Insurance Policy',
                filters: { name: frm.doc.policy },
                fieldname: 'name'
            },
            callback: function (r) {
                // We use frappe.model.get_doc to get the child table
                let policy = frappe.get_doc('Insurance Policy', frm.doc.policy);
                if (policy && policy.coverage_snapshot) {
                    let coverages = policy.coverage_snapshot.map(c => c.coverage_type);
                    frm.set_df_property('coverage_type', 'options', coverages.join('\n'));
                }
            }
        });
    },

    date_of_loss: function (frm) {
        if (frm.doc.date_of_loss && frm.doc.policy_start_date && frm.doc.policy_end_date) {
            let dol = frappe.datetime.str_to_obj(frm.doc.date_of_loss);
            let start = frappe.datetime.str_to_obj(frm.doc.policy_start_date);
            let end = frappe.datetime.str_to_obj(frm.doc.policy_end_date);

            if (dol < start || dol > end) {
                frappe.msgprint({
                    title: __('Validation Error'),
                    message: __('Date of Loss must be within Policy Period ({0} to {1})').format(frm.doc.policy_start_date, frm.doc.policy_end_date),
                    indicator: 'red'
                });
                frm.set_value('date_of_loss', '');
            }
        }
    }
});
