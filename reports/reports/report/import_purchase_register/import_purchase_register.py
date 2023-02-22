## Testing Feb 6 22:45
import frappe
def execute(filters=None):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    supplier = filters.get("supplier")
    if supplier:
        supplier_condition = "and pi.supplier = %(supplier)s"
    else:
        supplier_condition = ""
    columns = [
        "Posting Date:Date:100",
        "Supplier Id:Link/Supplier:100",
        "Supplier Name:Data:150",
        "Invoice:Data:150",
        "Bill of Entry No:Data:130",
        "Bill of Entry Date:Date:100",
        "Supplier Invoice No.:Data:150",
        "Supplier Invoice Date:Date:100",
        "Awb/BL No.:Data:150",
        "Assy. Value:Currency:100",
        "Port Code:Data:100",
        "Gate Entry No:Data:100",
        "Gate Entry Date:Date:100",
        "Invoice Amt. INR:Currency:130",
        "Invoice Amt. USD:Data:130",
        "Currency:Data:70",
        "Exchange Rate:Data:70",
        "Amount in INR:Currency:130",
        "Purchase Receipt No.:Data:150",
        "Total Taxes and Charges:Currency:150",
    ]
    
    data = frappe.db.sql("""
        select 
            pi.posting_date, 
            pi.supplier,
            pi.supplier_name, 
            pi.name, 
            pi.bill_of_entry_no, 
            pi.bill_of_entry_date, 
            pi.bill_no, 
            pi.bill_date, 
            pi.awb_bl_no, 
            pi.assy_value, 
            pi.port_code, 
            pr.gate_entry_no, 
            pr.gate_entry_date,
            pi.base_total,
            pi.total,
            pi.currency,
            pi.conversion_rate,
            pi.base_grand_total,
            pr.name
        from 
            `tabPurchase Invoice` pi 
            left join `tabPurchase Invoice Item` pii on pi.name = pii.parent
            left join `tabPurchase Receipt` pr on pii.purchase_receipt = pr.name

        where 
            pi.posting_date>=%(from_date)s and pi.posting_date<=%(to_date)s
            and pi.supplier in (select name from `tabSupplier` where supplier_group = 'Import Purchase')
            {supplier_condition}
        order by
            pi.posting_date desc
    """.format(supplier_condition=(supplier_condition) if supplier_condition else ""), {"from_date": from_date, "to_date": to_date, "supplier":supplier} ,as_list=1)

    for row in data:
        total_taxes_and_charges = frappe.db.sql("""
            select  
                lcv.total_taxes_and_charges,
                lctc.expense_account,
                lctc.amount
            from 
                `tabLanded Cost Voucher` lcv 
                left join `tabLanded Cost Purchase Receipt` lcpt on lcv.name = lcpt.parent
                left join `tabLanded Cost Taxes and Charges` lctc on lcv.name = lctc.parent
            where 
                lcpt.receipt_document = %s
        """, (row[18]), as_list=1)
        
        if(total_taxes_and_charges):            
            row.append(total_taxes_and_charges[0][0])
        else:
            row.append([0])

        for expense_account in total_taxes_and_charges:
        	if((expense_account[1] + ":Currency:150") not in columns):
        		columns.append(expense_account[1] + ":Currency:150")

        # get account and debit or credit amount from Journal Entry Account child table 
        # add account to columns if not present    
        journal_account = frappe.db.sql("""
            select
                jva.account
            from
                `tabJournal Entry` jv
                left join `tabJournal Entry Account` jva on jv.name = jva.parent
            where
                jva.custom_duty_invoice_ref = %s
        """, (row[3]), as_list=1)
        for account in journal_account:
            if((account[0] + ":Currency:150") not in columns):
                columns.append(account[0] + ":Currency:150")


    # insert none values in the row for the columns that are not present in the row
    total_taxes_index = columns.index('Total Taxes and Charges:Currency:150')

    # Loop over each row in the data list
    i = 0
    for row in data:
        # Add None values to the end of the row for any columns that come after 'Total Taxes and Charges'
        for i in range(total_taxes_index + 1, len(columns)):
            row.append(None)
        
    for row in data:
        total_taxes_and_charges = frappe.db.sql("""
            select  
                lcv.total_taxes_and_charges,
                lctc.expense_account,
                lctc.amount
            from 
                `tabLanded Cost Voucher` lcv 
                left join `tabLanded Cost Purchase Receipt` lcpt on lcv.name = lcpt.parent
                left join `tabLanded Cost Taxes and Charges` lctc on lcv.name = lctc.parent
            where 
                lcpt.receipt_document = %s
        """, (row[18]), as_list=1)

        for expense_account in total_taxes_and_charges:
            index = columns.index(expense_account[1] + ":Currency:150")
            if((expense_account[1] + ":Currency:150") in columns): 			
                row[index] =  expense_account[2]
    
        journal_account = frappe.db.sql("""
            select
                jva.account,
                jva.debit,
                jva.credit
            from
                `tabJournal Entry` jv
                left join `tabJournal Entry Account` jva on jv.name = jva.parent
            where
                jva.custom_duty_invoice_ref = %s
        """, (row[3]), as_list=1)
        for account in journal_account:
            index = columns.index(account[0] + ":Currency:150")
            if((account[0] + ":Currency:150") in columns):	
                if account[1] > 0:
                    row[index] =  account[1]
                else:
                    row[index] =  account[2]
    return columns, data


## Testing Feb 6 22:45
