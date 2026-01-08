// Copyright (c) 2026, DharmendraInsurance Solutions Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle', {
    refresh: function (frm) {
        if (!frm.is_new() && frm.doc.rc_raw_data && frappe.user.name !== 'Administrator') {
            // Lock critical fields if data was fetched from API
            const locked_fields = ['make', 'model', 'variant', 'chassis_number', 'engine_number',
                'manufacturing_year', 'fuel_type', 'vehicle_type', 'registration_number'];
            locked_fields.forEach(field => {
                frm.set_df_property(field, 'read_only', 1);
            });
        }
    },

    fetch_vehicle_details: function (frm) {
        if (!frm.doc.registration_number) {
            frappe.throw(__("Please enter Registration Number first."));
            return;
        }

        frappe.call({
            method: "insurance_erp.api.fetch_vehicle_rc",
            args: {
                reg_no: frm.doc.registration_number
            },
            freeze: true,
            freeze_message: __("Fetching from Cashfree..."),
            callback: function (r) {
                if (r.message) {
                    const data = r.message;

                    // Cashfree response structure might vary, mapping common fields
                    // Assuming response like: { "status": "VALID", "vehicle_chassis_number": "...", ... }

                    // If the response is wrapped (e.g. data.result or data.data) adjust accordingly
                    // For now mapping top-level logic based on standard response

                    if (data.vehicle_chassis_number) {
                        frm.set_value('chassis_number', data.vehicle_chassis_number);
                    }
                    if (data.vehicle_engine_number) {
                        frm.set_value('engine_number', data.vehicle_engine_number);
                    }
                    if (data.vehicle_manufacturer_name) {
                        frm.set_value('make', data.vehicle_manufacturer_name);
                    }
                    if (data.model) {
                        frm.set_value('model', data.model);
                    }
                    if (data.vehicle_fuel_type) {
                        // Map standard fuels to our Select options
                        let fuel = data.vehicle_fuel_type.toUpperCase();
                        if (fuel.includes('PETROL')) frm.set_value('fuel_type', 'Petrol');
                        else if (fuel.includes('DIESEL')) frm.set_value('fuel_type', 'Diesel');
                        else if (fuel.includes('CNG')) frm.set_value('fuel_type', 'CNG');
                        else if (fuel.includes('ELECTRIC')) frm.set_value('fuel_type', 'Electric');
                        else if (fuel.includes('HYBRID')) frm.set_value('fuel_type', 'Hybrid');
                    }
                    if (data.vehicle_manufacturing_date) {
                        try {
                            let year = new Date(data.vehicle_manufacturing_date).getFullYear();
                            frm.set_value('manufacturing_year', year);
                        } catch (e) { console.log("Date parse error", e); }
                    }
                    if (data.owner_name) {
                        frm.set_value('owner_name', data.owner_name);
                    }
                    if (data.vehicle_registration_date) {
                        frm.set_value('registration_date', data.vehicle_registration_date);
                    }

                    // Set Status fields
                    if (data.rc_status) frm.set_value('rc_status', data.rc_status);
                    if (data.blacklist_status) frm.set_value('blacklist_status', data.blacklist_status);

                    // Save Raw JSON
                    frm.set_value('rc_raw_data', JSON.stringify(data, null, 4));

                    frappe.msgprint({
                        title: __('Success'),
                        indicator: 'green',
                        message: __('Vehicle details fetched successfully.')
                    });
                }
            }
        });
    }
});
