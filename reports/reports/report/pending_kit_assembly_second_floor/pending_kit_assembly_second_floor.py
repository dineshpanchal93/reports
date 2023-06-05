# Copyright (c) 2023, dineshpanchal432@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

# creation_date
# production_item
# item_name
# qty as kit_issued
# produced_qty
# balance_qty = qty - produced_qty


def get_data(filters):
    work_order = frappe.qb.DocType("Work Order")
    query = (
		frappe.qb.from_(work_order)
		.select(
			work_order.name,
			work_order.creation,
			work_order.production_item,
			work_order.item_name,
			work_order.qty.as_("kit_issued"),
			work_order.produced_qty,
			(work_order.qty - work_order.produced_qty).as_("balance_qty"),
		).where(work_order.docstatus == 1)
		.where(work_order.status == "In Process")
		.where(work_order.fg_warehouse == "Assembly 2nd Floor OQC - BEPL")
		)
    
	# Apply additional filters
    if filters.get("from_date"):
        query = query.where(work_order.creation >= filters.get("from_date"))
    if filters.get("to_date"):
        query = query.where(work_order.creation <= filters.get("to_date"))
    if filters.get("production_item"):
        query = query.where(work_order.production_item == filters.get("production_item"))

    
    return query.run(as_dict=True)


def get_columns(filters):
    
    columns = [
        {
            "label": _("Work Order"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Work Order",
            "width": 150,
		},
		{
			"label": _("Creation Date"),
			"fieldname": "creation",
			"fieldtype": "Date",
			"width": 150,
		},
		{
			"label": _("Production Item"),
			"fieldname": "production_item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 250,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 400,
		},
		{
			"label": _("Kit Issued"),
			"fieldname": "kit_issued",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Produced Qty"),
			"fieldname": "produced_qty",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Balance Qty"),
			"fieldname": "balance_qty",
			"fieldtype": "Float",
			"width": 150,
		},
    ]
    
    return columns
    
	
        
        
    