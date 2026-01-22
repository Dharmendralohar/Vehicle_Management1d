frappe.pages['all-claims'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'All Claims',
		single_column: true
	});

	page.set_primary_action('Refresh', () => render_claims(page));

	render_claims(page);
}

frappe.templates["all_claims"] = `
<div class="row">
    <div class="col-md-12">
        <div class="frappe-card">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead class="text-muted">
                        <tr>
                            <th>Claim Number</th>
                            <th>Policy</th>
                            <th>Status</th>
                            <th>Nature of Loss</th>
                            <th>Date of Loss</th>
                            <th class="text-right">Claim Amount</th>
                            <th class="text-right">Approved Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for(var i=0, l=claims.length; i<l; i++) { 
                           var c = claims[i]; %}
                        <tr class="claim-row" data-name="{{ c.name }}" style="cursor: pointer;">
                            <td class="font-weight-bold text-primary">{{ c.name }}</td>
                            <td>{{ c.policy }}</td>
                            <td>
                                <span class="indicator-pill {{ c.status_class }}">
                                    {{ c.status }}
                                </span>
                            </td>
                            <td>{{ c.nature_of_loss }}</td>
                            <td>{{ c.date_of_loss_formatted }}</td>
                            <td class="text-right">{{ c.claim_amount_formatted }}</td>
                            <td class="text-right">{{ c.approved_amount_formatted }}</td>
                        </tr>
                        {% } %}
                        {% if(!claims.length) { %}
                        <tr>
                            <td colspan="7" class="text-center text-muted p-5">
                                No Claims Found.
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

function render_claims(page) {
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Insurance Claim",
			fields: ["name", "policy", "status", "nature_of_loss", "date_of_loss", "claim_amount", "approved_amount"],
			order_by: "creation desc"
		},
		callback: function (r) {
			let claims = r.message || [];

			// Pre-process data for template
			claims.forEach(function (c) {
                // Status Colors
                if(c.status === 'Reported') c.status_class = 'red';
                else if(c.status === 'Surveyor Appointed') c.status_class = 'orange';
                else if(c.status === 'Admitted' || c.status === 'Approved') c.status_class = 'blue';
                else if(c.status === 'Settled') c.status_class = 'green';
                else c.status_class = 'gray';

				c.date_of_loss_formatted = frappe.datetime.str_to_user(c.date_of_loss);
				c.claim_amount_formatted = format_currency(c.claim_amount, "INR");
                c.approved_amount_formatted = format_currency(c.approved_amount || 0, "INR");
			});

			let html = frappe.render_template("all_claims", { claims: claims });
			$(page.body).html(html);

			// Add Click Event
			$(page.body).find('.claim-row').on('click', function () {
				let claim_name = $(this).data('name');
				frappe.set_route('Form', 'Insurance Claim', claim_name);
			});
		}
	});
}
