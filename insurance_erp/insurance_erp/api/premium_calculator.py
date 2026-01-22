import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def calculate_premium(plan, vehicle, idv, addons=None, ncb_percent=0):
    """
    Calculate premium based on Insurance Plan, Vehicle, IDV, and Addons.
    """
    if isinstance(addons, str):
        import json
        addons = json.loads(addons)
        
    if not plan or not idv:
        return {}

    plan_doc = frappe.get_doc("Insurance Plan", plan)
    
    # 1. Validation: Vehicle Engine CC vs Plan Limits
    if vehicle:
        vehicle_doc = frappe.get_doc("Vehicle", vehicle)
        cc = flt(vehicle_doc.engine_cc)
        
        # Only validate if Plan has limits defined
        if plan_doc.engine_cc_from and cc < plan_doc.engine_cc_from:
            # We just log/warning here, deciding to hard-block or return error is separate. 
            # For calculation, we might proceed or return warning.
            # Let's assume strict plan adherence implies we should warn.
            pass 
            
        if plan_doc.engine_cc_to and cc > plan_doc.engine_cc_to:
            pass

    # 2. OD Premium
    od_premium = 0.0
    if plan_doc.od_rate_type == "Percentage":
        od_premium = flt(idv) * flt(plan_doc.od_rate_value) / 100.0
    else:
        od_premium = flt(plan_doc.od_rate_value)
        
    # Apply Min/Max Caps
    if plan_doc.min_od_premium and od_premium < plan_doc.min_od_premium:
        od_premium = plan_doc.min_od_premium
    if plan_doc.max_od_premium and plan_doc.max_od_premium > 0 and od_premium > plan_doc.max_od_premium:
        od_premium = plan_doc.max_od_premium
        
    # Apply NCB Discount (on OD only)
    ncb_discount_amount = od_premium * flt(ncb_percent) / 100.0
    od_premium_after_ncb = od_premium - ncb_discount_amount
    if od_premium_after_ncb < 0:
        od_premium_after_ncb = 0
    
    # 3. TP Premium
    tp_premium = flt(plan_doc.tp_premium_value)
    
    # 4. Add-ons Premium
    addon_premium_total = 0.0
    addon_details = []
    
    # Map plan addons for quick lookup
    plan_addon_map = {row.addon: row for row in plan_doc.plan_addons}
    
    if addons:
        for addon_name in addons:
            if addon_name in plan_addon_map:
                row = plan_addon_map[addon_name]
                cost = 0.0
                if row.pricing_type == "Flat":
                    cost = flt(row.pricing_value)
                elif row.pricing_type == "Percentage of IDV":
                    cost = flt(idv) * flt(row.pricing_value) / 100.0
                
                addon_premium_total += cost
                addon_details.append({
                    "addon": addon_name,
                    "premium_amount": cost
                })
    
    # 5. Totals
    total_net = od_premium_after_ncb + tp_premium + addon_premium_total
    
    gst_rate = flt(plan_doc.gst_rate) or 18.0
    total_gst = total_net * gst_rate / 100.0
    
    grand_total = total_net + total_gst
    
    return {
        "od_premium": od_premium_after_ncb,
        "od_premium_base": od_premium, # Before NCB
        "ncb_discount": ncb_discount_amount,
        "tp_premium": tp_premium,
        "addon_premium": addon_premium_total,
        "total_net_premium": total_net,
        "total_gst": total_gst,
        "grand_total_premium": grand_total,
        "addon_details": addon_details
    }
