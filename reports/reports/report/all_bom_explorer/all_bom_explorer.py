# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.utils import logger

logger.set_log_level("DEBUG")
logger = frappe.logger("all bom explorer", allow_site=True, file_count=1)


def execute(filters=None):
	data = []
	columns = get_columns()
	get_data(data, filters)
	return columns, data


def get_data(data, filters):
	if not filters.get("bom"):
		boms = frappe.get_all("BOM", filters={"is_default": 1, "is_active": 1, "docstatus": 1, "name": ["like", "%fa%"]},  fields=["name"])
		for bom in boms:
			logger.info(f"BOM: {bom.name}")
			get_exploded_items(data, bom.name)
	else:
		get_exploded_items(data, filters.get("bom"))


def get_exploded_items(data, bom, indent=0, qty=1):
    exploded_items = frappe.get_all(
        "BOM Item",
        filters={"parent": bom},
        fields=["qty", "bom_no", "item_code", "item_name", "description", "uom", "rate", "amount"],
        order_by="idx asc",
    )

    index = 1
 
    for item in exploded_items:
        item["indent"] = indent
        if index == 1 and indent == 0:
            parent_bom = bom
            item_code = f"<b>{parent_bom}</b>"
        else:
            parent_bom = ""
            item_code = item.item_code
        if not item.bom_no:
            data.append(
                {
                    "parent_bom": f"<b>{parent_bom}</b>",
                    "item_code": item_code,
                    "item_name": item.item_name,
                    "indent": indent,
                    "bom_level": indent,
                    "bom": item.bom_no,
                    "qty": item.qty * qty,
                    "uom": item.uom,
                    "rate": item.rate,
                    "amount": item.amount,
                    "description": item.description,
                }
            )

        else:
            sub_bom = frappe.get_value("BOM", filters={"name": item.bom_no, "is_default": 1, "is_active": 1, "docstatus": 1})
            if sub_bom:
                data.append(
                    {
                        "parent_bom": f"<b>{parent_bom}</b>",
                        "item_code": item_code,
                        "item_name": item.item_name,
                        "indent": indent,
                        "bom_level": indent,
                        "bom": item.bom_no,
                        "qty": item.qty * qty,
                        "uom": item.uom,
                        "rate": 0,
                        "amount": 0,
                        "description": item.description,
                    }
                )
                if item.bom_no:
                    get_exploded_items(data, item.bom_no, indent=indent + 1, qty=item.qty)

        index += 1




def get_columns():
	return [
		{
			"label": _("Item Code"),
			"fieldtype": "Link",
			"fieldname": "item_code",
			"width": 300,
			"options": "Item",
		},
		{"label": _("Item Name"), "fieldtype": "data", "fieldname": "item_name",  "width": 250},
		{"label": _("Parent BOM"), "fieldtype": "Link", "fieldname": "parent_bom", "options": "BOM","width": 220},

		{"label": _("Child BOM"), "fieldtype": "Link", "fieldname": "bom", "width": 220, "options": "BOM"},
		{"label": _("Qty"), "fieldtype": "data", "fieldname": "qty", "width": 100},
		{"label": _("UOM"), "fieldtype": "data", "fieldname": "uom", "width": 100},
		{"label": _("Rate"), "fieldtype": "data", "fieldname": "rate", "width": 100},
		{"label": _("Amount"), "fieldtype": "data", "fieldname": "amount", "width": 100},
		{"label": _("BOM Level"), "fieldtype": "Int", "fieldname": "bom_level", "width": 100},
		{
			"label": _("Standard Description"),
			"fieldtype": "data",
			"fieldname": "description",
			"width": 150,
		},
	]
