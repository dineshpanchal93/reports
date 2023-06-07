// Copyright (c) 2023, dineshpanchal432@gmail.com and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOM Explorer Rate-Amount"] = {
	"filters": [
		{
			fieldname: "bom",
			label: __("BOM"),
			fieldtype: "Link",
			options: "BOM",
			reqd: 1
		},
	]
};
