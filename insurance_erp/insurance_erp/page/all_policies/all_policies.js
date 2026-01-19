frappe.pages['all-policies'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'All Policies',
		single_column: true
	});

	page.set_primary_action('Refresh', () => render_policies(page));

	render_policies(page);
}

frappe.templates["all_policies"] = `
<div class="row">
    <div class="col-md-12">
        <div class="frappe-card">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="text-muted">
                        <tr>
                            <th>Policy Number</th>
                            <th>Customer</th>
                            <th>Status</th>
                            <th>Start Date</th>
                            <th>End Date</th>
                            <th>Vehicle</th>
                            <th class="text-right">Premium Paid</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for(var i=0, l=policies.length; i<l; i++) { 
                           var p = policies[i]; %}
                        <tr class="policy-row" data-name="{{ p.name }}" style="cursor: pointer;">
                            <td class="font-weight-bold text-primary">{{ p.name }}</td>
                            <td>{{ p.customer }}</td>
                            <td>
                                <span class="indicator-pill {{ p.status_class }}">
                                    {{ p.status }}
                                </span>
                            </td>
                            <td>{{ p.start_date_formatted }}</td>
                            <td>{{ p.end_date_formatted }}</td>
                            <td>{{ p.vehicle || '-' }}</td>
                            <td class="text-right">{{ p.premium_formatted }}</td>
                        </tr>
                        {% } %}
                        {% if(!policies.length) { %}
                        <tr>
                            <td colspan="7" class="text-center text-muted p-5">
                                No Policies Found.
                            </td>
                        </tr>
                        {% } %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
`;

function render_policies(page) {
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Insurance Policy",
			fields: ["name", "customer", "status", "policy_start_date", "policy_end_date", "premium_paid", "vehicle"],
			order_by: "creation desc"
		},
		callback: function (r) {
			let policies = r.message || [];

			// Pre-process data for template
			policies.forEach(function (p) {
				p.status_class = (p.status === 'Active') ? 'green' : 'red';
				p.start_date_formatted = frappe.datetime.str_to_user(p.policy_start_date);
				p.end_date_formatted = frappe.datetime.str_to_user(p.policy_end_date);
				p.premium_formatted = format_currency(p.premium_paid, "INR");
			});

			let html = frappe.render_template("all_policies", { policies: policies });
			$(page.body).html(html);

			// Add Click Event
			$(page.body).find('.policy-row').on('click', function () {
				let policy_name = $(this).data('name');
				frappe.set_route('Form', 'Insurance Policy', policy_name);
			});
		}
	});
}																																																																																																																	