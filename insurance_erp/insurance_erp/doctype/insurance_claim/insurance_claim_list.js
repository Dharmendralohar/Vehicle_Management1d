frappe.listview_settings['Insurance Claim'] = {
    add_fields: ["status", "customer", "vehicle"],
    get_indicator: function (doc) {
        if (doc.status === "Reported") {
            return [__("Reported"), "blue", "status,=,Reported"];
        } else if (doc.status === "Survey Assigned") {
            return [__("Survey Assigned"), "orange", "status,=,Survey Assigned"];
        } else if (doc.status === "Survey Completed") {
            return [__("Survey Completed"), "green", "status,=,Survey Completed"];
        } else if (doc.status === "Approved") {
            return [__("Approved"), "green", "status,=,Approved"];
        } else if (doc.status === "Rejected") {
            return [__("Rejected"), "red", "status,=,Rejected"];
        } else if (doc.status === "Settled") {
            return [__("Settled"), "blue", "status,=,Settled"];
        }
    },
    onload: function (listview) {
        listview.page.add_inner_button(__("Move to Survey"), function () {
            let selected_claims = listview.get_checked_items();
            if (selected_claims.length === 0) {
                frappe.throw(__("Please select at least one claim"));
            }

            // Filter for only 'Reported' claims
            let valid_claims = selected_claims.filter(d => d.status === 'Reported').map(d => d.name);
            if (valid_claims.length === 0) {
                frappe.throw(__("Only claims in 'Reported' status can be moved to Survey"));
            }

            let d = new frappe.ui.Dialog({
                title: __("Assign Surveyor"),
                fields: [
                    {
                        label: __("Surveyor"),
                        fieldname: "surveyor",
                        fieldtype: "Link",
                        options: "User",
                        reqd: 1
                    },
                    {
                        label: __("Survey Date"),
                        fieldname: "survey_date",
                        fieldtype: "Date",
                        default: frappe.datetime.nowdate(),
                        reqd: 1
                    },
                    {
                        label: __("Claims Selected"),
                        fieldname: "info",
                        fieldtype: "HTML",
                        options: `<p>Assigning surveyor to <b>${valid_claims.length}</b> selected claims: <br><small>${valid_claims.join(", ")}</small></p>`
                    }
                ],
                primary_action_label: __("Confirm Assignment"),
                primary_action(values) {
                    frappe.call({
                        method: "insurance_erp.events.assign_surveyor_to_claims",
                        args: {
                            claim_names: valid_claims,
                            surveyor: values.surveyor,
                            survey_date: values.survey_date
                        },
                        callback: function (r) {
                            if (r.message) {
                                let success_count = r.message.filter(res => res.status === "Success").length;
                                frappe.show_alert({
                                    message: __("{0} Claims successfully moved to Survey").format(success_count),
                                    indicator: "green"
                                });
                                listview.refresh();
                                d.hide();
                            }
                        }
                    });
                }
            });
            d.show();
        });
    }
};
