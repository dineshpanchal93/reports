from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import PaymentReconciliation
from frappe.utils import flt
import frappe

class CustomPaymentReconciliation(PaymentReconciliation):
    def add_invoice_entries(self, non_reconciled_invoices):
        # Populate 'invoices' with JVs and Invoices to reconcile against
        self.set("invoices", [])
        non_reconciled_invoices = sorted(non_reconciled_invoices, key=lambda k: k['voucher_no'])

        for entry in non_reconciled_invoices:
            inv = self.append("invoices", {})
            inv.invoice_type = entry.get("voucher_type")
            inv.invoice_number = entry.get("voucher_no")
            inv.invoice_date = entry.get("posting_date")
            inv.amount = flt(entry.get("invoice_amount"))
            inv.currency = entry.get("currency")
            inv.outstanding_amount = flt(entry.get("outstanding_amount"))

        # frappe.msgprint(":: Sorting Done ::")
        super().add_invoice_entries(non_reconciled_invoices)

