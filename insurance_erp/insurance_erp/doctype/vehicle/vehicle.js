// Copyright (c) 2026, DharmendraInsurance Solutions Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on('Vehicle', {
    refresh: function (frm) {
        // No special refresh logic needed yet for simple blocking
    },

    fetch_rc_details: function (frm) {
        if (!frm.doc.registration_no) {
            frappe.throw(__("Please enter Registration No first."));
            return;
        }

        frappe.call({
            method: "insurance_erp.api.fetch_vehicle_rc",
            args: {
                reg_no: frm.doc.registration_no
            },
            freeze: true,
            freeze_message: __("Verifying with Cashfree..."),
            callback: function (r) {
                if (r.message && r.message.status === 'SUCCESS') {
                    const data = r.message.data;

                    if (data.vehicle_chassis_number) {
                        frm.set_value('chassis_no', data.vehicle_chassis_number);
                    }
                    if (data.vehicle_engine_number) {
                        frm.set_value('engine_no', data.vehicle_engine_number);
                    }
                    if (data.vehicle_manufacturer_name) {
                        frm.set_value('make', data.vehicle_manufacturer_name);
                    }
                    if (data.model) {
                        frm.set_value('model', data.model);
                    }
                    if (data.vehicle_fuel_type) {
                        let fuel = data.vehicle_fuel_type.toUpperCase();
                        if (fuel.includes('PETROL')) frm.set_value('fuel_type', 'Petrol');
                        else if (fuel.includes('DIESEL')) frm.set_value('fuel_type', 'Diesel');
                        else if (fuel.includes('CNG')) frm.set_value('fuel_type', 'CNG');
                        else if (fuel.includes('ELECTRIC')) frm.set_value('fuel_type', 'Electric');
                        else if (fuel.includes('HYBRID')) frm.set_value('fuel_type', 'Hybrid');
                        else if (fuel.includes('LPG')) frm.set_value('fuel_type', 'LPG');
                    }
                    if (data.vehicle_class) {
                        frm.set_value('vehicle_class', data.vehicle_class);
                    }
                    if (data.rc_status) {
                        frm.set_value('rc_status', data.rc_status.toUpperCase());
                    }
                    if (data.vehicle_registration_date_expiry) {
                        frm.set_value('rc_expiry_date', data.vehicle_registration_date_expiry);
                    }

                    frm.set_value('rc_verified', 1);
                    frm.set_value('rc_api_reference_id', data.reference_id || '');
                    frm.set_value('rc_raw_response', r.message.raw_response);

                    frappe.msgprint({
                        title: __('Success'),
                        indicator: 'green',
                        message: __('Vehicle RC verified successfully.')
                    });
                } else if (r.message && r.message.status === 'ERROR') {
                    frm.set_value('rc_verified', 0);
                    frm.set_value('rc_raw_response', r.message.raw_response);
                    frappe.msgprint({
                        title: __('Verification Failed'),
                        indicator: 'red',
                        message: r.message.message
                    });
                } else if (r.message && r.message.status === 'TIMEOUT') {
                    frappe.msgprint({
                        title: __('Timeout'),
                        indicator: 'orange',
                        message: __('API request timed out. Please try again or verify manually if allowed.')
                    });
                }
            }
        });
    }
});
