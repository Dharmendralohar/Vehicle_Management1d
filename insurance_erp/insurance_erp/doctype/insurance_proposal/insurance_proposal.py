# Copyright (c) 2026, Insurance Solutions Inc and contributors
# For license information, please see license.txt

import frappe
from frappe import _, bold
from frappe.model.document import Document
from frappe.utils import getdate, today, date_diff, flt

class InsuranceProposal(Document):
	def validate(self):
		"""Validate proposal before submission"""
		self.validate_mandatory_vehicle_data()
		self.calculate_vehicle_age()
		self.calculate_idv()
		self.calculate_premium_breakdown()
		self.validate_dates()

	def validate_mandatory_vehicle_data(self):
		"""Ensure all mandated vehicle fields are present and mandatory in the linked Vehicle record"""
		if not self.vehicle:
			frappe.throw(_("Please select a Vehicle first."))

		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		
		# List of mandatory fields derived from PDF standards
		mandatory_fields = {
			"license_plate": "Registration Number",
			"custom_rto_location": "RTO Location",
			"custom_vehicle_category": "Vehicle Category",
			"make": "Manufacturer",
			"model": "Model",
			"custom_body_type": "Body Type",
			"custom_engine_cc": "Engine CC",
			"custom_manufacturing_year": "Manufacturing Year",
			"custom_seating_capacity": "Seating Capacity",
			"custom_engine_number": "Engine Number",
			"chassis_no": "Chassis Number",
			"fuel_type": "Fuel Type",
			"custom_vehicle_idv": "Insured Declared Value (IDV)",
			"vehicle_value": "Vehicle Value"
		}

		missing = []
		for field, label in mandatory_fields.items():
			if not vehicle.get(field):
				missing.append(label)

		if missing:
			frappe.throw(
				_("Cannot proceed with Proposal {0}. The following mandatory vehicle data is missing in linked Vehicle {1}: {2}").format(
					bold(self.name), bold(self.vehicle), bold(", ".join(missing))
				)
			)
		
		# Sync vehicle value for snapshot
		self.vehicle_value_snapshot = vehicle.vehicle_value

	def calculate_vehicle_age(self):
		"""Derive vehicle age from manufacturing year"""
		vehicle = frappe.get_doc("Vehicle", self.vehicle)
		current_year = getdate(today()).year
		self.vehicle_age = flt(current_year - vehicle.custom_manufacturing_year, 2)
		if self.vehicle_age < 0:
			frappe.throw(_("Manufacturing Year ({0}) cannot be in the future.").format(vehicle.custom_manufacturing_year))

	def calculate_idv(self):
		"""Calculate Insured Declared Value (IDV) based on plan rules and depreciation"""
		if not self.insurance_plan:
			return

		plan = frappe.get_doc("Insurance Plan", self.insurance_plan)
		vehicle_value = self.vehicle_value_snapshot or 0
		
		# Find applicable depreciation percent from slabs
		age_months = self.vehicle_age * 12
		depreciation_percent = 0
		
		for slab in plan.get("depreciation_slabs", []):
			if age_months >= slab.from_age_months and age_months <= (slab.to_age_months or 999):
				depreciation_percent = slab.depreciation_percent
				break
		
		self.calculated_idv = flt(vehicle_value * (1 - (depreciation_percent / 100)), 2)

	def calculate_premium_breakdown(self):
		"""Sum OD, TP, and Add-ons for total premium payable"""
		self.total_premium_payable = flt(
			(self.own_damage_premium or 0) + 
			(self.third_party_premium or 0) + 
			(self.addon_premium or 0) + 
			(self.tax_amount or 0),
			2
		)

	def validate_dates(self):
		if not self.policy_duration_from or not self.policy_duration_to:
			frappe.throw(_("Policy Duration From and To are mandatory"))
		
		if getdate(self.policy_duration_to) <= getdate(self.policy_duration_from):
			frappe.throw(_("Policy Duration To must be after Policy Duration From"))

@frappe.whitelist()
def create_policy_from_proposal(proposal_name):
	"""Create Insurance Policy from approved proposal with data freezing"""
	proposal = frappe.get_doc("Insurance Proposal", proposal_name)
	
	if proposal.status != "Approved":
		frappe.throw(_("Only Approved proposals can be converted to policies"))
	
	existing_policy = frappe.db.exists("Insurance Policy", {"insurance_proposal": proposal_name})
	if existing_policy:
		frappe.throw(_("A policy already exists for this proposal: {0}").format(existing_policy))
	
	policy = frappe.new_doc("Insurance Policy")
	policy.customer = proposal.customer
	policy.insurance_proposal = proposal.name
	policy.insurance_plan = proposal.insurance_plan
	policy.vehicle = proposal.vehicle
	policy.vehicle_idv = proposal.calculated_idv
	policy.policy_start_date = proposal.policy_duration_from
	policy.policy_end_date = proposal.policy_duration_to
	
	# Fix: Generate Policy Number from Settings
	settings = frappe.get_single("Insurance System Settings")
	series = settings.policy_naming_series or "POL-.YYYY.-"
	from frappe.model.naming import make_autoname
	policy.policy_number = make_autoname(series)

	# Freeze Premium Snapshot
	policy.own_damage_premium = proposal.own_damage_premium
	policy.third_party_premium = proposal.third_party_premium
	policy.addon_premium = proposal.addon_premium
	policy.tax_amount = proposal.tax_amount
	policy.total_premium_payable = proposal.total_premium_payable
	
	policy.status = "Pending Payment"
	
	policy.insert(ignore_permissions=True)
	frappe.db.commit()
	
	return policy.name
