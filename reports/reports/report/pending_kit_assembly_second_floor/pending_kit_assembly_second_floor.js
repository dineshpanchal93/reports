// Copyright (c) 2023, dineshpanchal432@gmail.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Pending Kit Assembly Second Floor"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.month_start(),
			"width": "80"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.month_end(),
			"width": "80"
		},
		{
			"fieldname": "production_item",
			"label": __("Production Item"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "80"
		},

	]
};
