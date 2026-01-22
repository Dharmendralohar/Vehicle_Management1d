import frappe

def setup_client_script():
    script_content = """
frappe.ui.form.on('Sales Order', {
    setup: function(frm) {
        frm.set_query("vehicle", function() {
            return {
                filters: {
                    customer: frm.doc.customer
                }
            };
        });
        
        frm.set_query("insurance_plan", function() {
            return {
                filters: {
                    active: 1
                }
            };
        });
    },
    
    is_insurance_proposal: function(frm) {
        frm.toggle_reqd("insurance_plan", frm.doc.is_insurance_proposal);
        frm.toggle_reqd("vehicle", frm.doc.is_insurance_proposal);
        frm.toggle_reqd("idv", frm.doc.is_insurance_proposal);
    },
    
    insurance_plan: function(frm) {
        if (frm.doc.insurance_plan && frm.doc.is_insurance_proposal) {
             // Auto add item if not exists
             const item_code = frm.doc.insurance_plan; 
             // We assume Item Code matches Plan Name. 
             // Ideally we should check if the item exists, but add_child doesn't validate instantly.
             
             const existing = (frm.doc.items || []).find(i => i.item_code === item_code);
             if (!existing) {
                 const row = frm.add_child("items");
                 frappe.model.set_value(row.doctype, row.name, "item_code", item_code);
                 frappe.model.set_value(row.doctype, row.name, "qty", 1);
                 frappe.model.set_value(row.doctype, row.name, "delivery_date", frm.doc.delivery_date || frappe.datetime.get_today());
             }
        }
        frm.trigger('calculate_premium');
    },
    
    idv: function(frm) {
        frm.trigger('calculate_premium');
    },
    
    ncb_percent: function(frm) {
        frm.trigger('calculate_premium');
    },
    
    calculate_premium: function(frm) {
        if (!frm.doc.is_insurance_proposal || !frm.doc.insurance_plan || !frm.doc.idv) return;

        let addons = [];
        if (frm.doc.proposal_addons) {
            addons = frm.doc.proposal_addons.map(row => row.addon);
        }

        frappe.call({
            method: "insurance_erp.insurance_erp.api.premium_calculator.calculate_premium",
            args: {
                plan: frm.doc.insurance_plan,
                vehicle: frm.doc.vehicle,
                idv: frm.doc.idv,
                addons: JSON.stringify(addons),
                ncb_percent: frm.doc.ncb_percent
            },
            callback: function(r) {
                if (r.message) {
                    frm.set_value("od_premium", r.message.od_premium);
                    frm.set_value("tp_premium", r.message.tp_premium);
                    frm.set_value("addon_premium", r.message.addon_premium);
                    frm.set_value("total_net_premium", r.message.total_net_premium);
                    frm.set_value("total_gst", r.message.total_gst);
                    frm.set_value("grand_total_premium", r.message.grand_total_premium);
                    
                    if (r.message.addon_details) {
                        r.message.addon_details.forEach(det => {
                            let row = (frm.doc.proposal_addons || []).find(d => d.addon === det.addon);
                            if (row) {
                                frappe.model.set_value(row.doctype, row.name, "premium_amount", det.premium_amount);
                            }
                        });
                        frm.refresh_field("proposal_addons");
                    }
                    
                    // Update Item Rate logic in Client Script for immediate feedback
                    // Find the plan item
                    let items = frm.doc.items || [];
                    let plan_item = items.find(i => i.item_code === frm.doc.insurance_plan);
                    if (plan_item) {
                        frappe.model.set_value(plan_item.doctype, plan_item.name, "rate", r.message.total_net_premium);
                    }
                }
            }
        });
    }
});

frappe.ui.form.on('Proposal Addon', {
    proposal_addons_remove: function(frm) {
        frm.trigger('calculate_premium');
    },
    addon: function(frm) {
         frm.trigger('calculate_premium');
    }
});
    """
    
    doc_name = "Insurance Proposal Logic"
    if not frappe.db.exists("Client Script", doc_name):
        doc = frappe.new_doc("Client Script")
        doc.dt = "Sales Order"
        doc.view = "Form"
        doc.script = script_content
        doc.enabled = 1
        doc.name = doc_name
    else:
        doc = frappe.get_doc("Client Script", doc_name)
        doc.script = script_content
        doc.enabled = 1
        
    doc.save()
    frappe.db.commit()

if __name__ == "__main__":
    setup_client_script()
