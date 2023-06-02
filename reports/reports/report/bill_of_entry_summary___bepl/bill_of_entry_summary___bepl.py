# Copyright (c) 2023, Resilient Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
#  import logger
from frappe.utils import logger

logger.set_log_level("DEBUG")
logger = frappe.logger("bill_of_entry", allow_site=True, file_count=1)

def execute(filters=None):
    validate_filters(filters)
    if not filters:
        filters = {}

    return get_columns(), get_data(filters)


def validate_filters(filters=None):
    if filters is None:
        filters = {}
    filters = frappe._dict(filters)

    if not filters.company:
        frappe.throw(
            _("{} is mandatory for generating Bill of Entry Summary Report").format(
                _("Company")
            ),
            title=_("Invalid Filter"),
        )
    if not filters.from_date or not filters.to_date:
        frappe.throw(
            _(
                "From Date & To Date is mandatory for generating e-Invoice Summary"
                " Report"
            ),
            title=_("Invalid Filter"),
        )
    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date must be before To Date"), title=_("Invalid Filter"))


def get_data(filters):
    bill_of_entry = frappe.qb.DocType("Bill of Entry")
    journal_entry_account = frappe.qb.DocType("Journal Entry Account")
    purchase_invoice = frappe.qb.DocType("Purchase Invoice") 
    landed_cost_voucher = frappe.qb.DocType("Landed Cost Voucher")
    landed_cost_purchase_receipt = frappe.qb.DocType("Landed Cost Purchase Receipt")
    landed_cost_taxes_and_charges = frappe.qb.DocType("Landed Cost Taxes and Charges")
    purchase_invoice_item = frappe.qb.DocType("Purchase Invoice Item")

    query = (
        frappe.qb.from_(bill_of_entry)
        .select(
            bill_of_entry.name,
            bill_of_entry.purchase_invoice,
            bill_of_entry.bill_of_entry_no,
            bill_of_entry.bill_of_entry_date,
            bill_of_entry.bill_of_lading_no,
            (bill_of_entry.total_taxable_value - bill_of_entry.total_customs_duty).as_(
                "total_assessable_value"
            ),
            bill_of_entry.total_customs_duty,
            bill_of_entry.total_taxes,
            bill_of_entry.total_amount_payable,
            journal_entry_account.parent.as_("payment_journal_entry"),
            purchase_invoice.supplier,
            purchase_invoice.supplier_name,
            purchase_invoice.posting_date,
            purchase_invoice.bill_no,
            purchase_invoice.bill_date,
            purchase_invoice.inward_gate_no,
            purchase_invoice.inward_gate_entry_date,
            landed_cost_taxes_and_charges.expense_account,
            landed_cost_taxes_and_charges.amount 
        )
        .where(bill_of_entry.docstatus == 1)
        .where(
            bill_of_entry.bill_of_entry_date[
                filters.get("from_date") : filters.get("to_date")
            ]
        )
        .where(bill_of_entry.company == filters.get("company"))
        .left_join(journal_entry_account)
        .on(bill_of_entry.name == journal_entry_account.reference_name)
        .left_join(purchase_invoice)
        .on(purchase_invoice.name == bill_of_entry.purchase_invoice)
        .left_join(purchase_invoice_item)
        .on(purchase_invoice_item.parent == purchase_invoice.name)
        .left_join(landed_cost_purchase_receipt)
        .on(landed_cost_purchase_receipt.receipt_document == purchase_invoice_item.purchase_receipt)
        .left_join(landed_cost_voucher)
        .on(landed_cost_voucher.name == landed_cost_purchase_receipt.parent)
        .left_join(landed_cost_taxes_and_charges)
        .on(landed_cost_taxes_and_charges.parent == landed_cost_voucher.name)
        
    )


    return query.run(as_dict=1)


def get_columns():
    return [
        {
            "fieldname": "supplier",
            "label": _("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 100,
        },
        {
			"fieldname": "supplier_name",
			"label": _("Supplier Name"),
			"fieldtype": "Data",
			"width": 150,
		},
        {
            "fieldname": "name",
            "label": _("Bill of Entry"),
            "fieldtype": "Link",
            "options": "Bill of Entry",
            "width": 140,
        },
        {
            "fieldname": "purchase_invoice",
            "label": _("Purchase Invoice"),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 130,
        },
        {
			"fieldname": "posting_date",
			"label": _("Posting Date"),
			"fieldtype": "Date",
			"width": 100,
		},
        {
			"fieldname": "bill_no",
			"label": _("Supplier Bill No."),
			"fieldtype": "Data",
			"width": 100,
		},
        {
			"fieldname": "bill_date",
			"label": _("Supplier Bill Date"),
			"fieldtype": "Date",
			"width": 100,
		},
        {
			"fieldname": "inward_gate_no",
			"label": _("Inward Gate No."),
			"fieldtype": "Data",
			"width": 100,
		},
        {
			"fieldname": "inward_gate_entry_date",
			"label": _("Inward Gate Entry Date"),
			"fieldtype": "Date",
			"width": 100,
		},
        {
            "fieldname": "bill_of_entry_no",
            "label": _("BOE No."),
            "fieldtype": "Link",
            "options": "Bill of Entry",
            "width": 80,
        },
        {
            "fieldname": "bill_of_entry_date",
            "label": _("BOE Date"),
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "fieldname": "bill_of_lading_no",
            "label": _("Bill of Lading No."),
            "fieldtype": "Data",
            "width": 80,
        },
        {
            "fieldname": "payment_journal_entry",
            "label": _("Journal Entry for Payment"),
            "fieldtype": "Link",
            "options": "Journal Entry",
            "width": 100,
        },
        {
            "fieldname": "total_assessable_value",
            "label": _("Total Assessable Value"),
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "fieldname": "total_customs_duty",
            "label": _("Total Customs Duty"),
            "fieldtype": "Currency",
            "width": 110,
        },
        {
            "fieldname": "total_taxes",
            "label": _("Total Taxes"),
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "fieldname": "total_amount_payable",
            "label": _("Amount Payable"),
            "fieldtype": "Currency",
            "width": 90,
        },
        {
            "fieldname": "expense_account",
            "label": _("Expense Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 230,
        },
        {
            "fieldname": "amount",
            "label": _("Amount"),
            "fieldtype": "Currency",
            "width": 100,
        },
    ]
