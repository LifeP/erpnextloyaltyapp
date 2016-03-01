import frappe
from frappe import _
def points_allocation(doc,method):
    pointscheck(doc)

    a=frappe.get_all("Rule Engine", fields=["rule_type","minimum_amount","points ","points_multiplication_factor","converted_rupees"], filters={"status":"Active","docstatus":1})
    # docstatus is 1 when document is submitted
    for i in a:
        if i.get('rule_type')=="Loyalty Points":
            # print "in loyality points foor loop"
            minamount=int(i.get('minimum_amount'))
            pointsawarded=int(i.get('points'))
            factor=int(i.get('points_multiplication_factor'))
            amount=int(doc.total)
            points=(amount*pointsawarded)/minamount
            a=factor*points
            doc.amount=amount
            if payment_check(doc):
                doc.points_earned=a
            else:
                frappe.throw(_("Payment incomplete please complete the payment"))
            doc.doc_no=doc.name
            rupees=int(i.get('converted_rupees'))

def checkmethod(doc):
		l1=[]
		for raw in doc.get("payment_method"):
			l1.append(raw.method)
		if "Points" in l1:
			return int(raw.points)
		else:
			return 0
def on_submit(doc,method):
    now=0
    customer=frappe.get_doc("Customer",doc.customer_mobile_no)
     #customer.set('Points Details',[])
    n1 = customer.append('points_table', {})
    n1.purchase_date=doc.transaction_date
    n1.points_earned=doc.points_earned
    if checkmethod(doc)==0:
        n1.points_consumed=0
    else:
        n1.points_consumed=checkmethod(doc)

    customer.save()

def pointscheck(doc):
		customer=frappe.get_doc("Customer",doc.customer_mobile_no)
		tpoint=customer.total_points
		#frappe.errprint(tpoint)
		for raw in doc.get("payment_method"):
			if raw.method=="Points":
				# frappe.errprint(tpoint)
				if int(raw.points) > int(tpoint):
					#frappe.errprint("#####True######")

					frappe.throw(_("Customer doesn't have enough points for redumption."))

def on_update(doc,method):
    if doc.get("payment_method"):
        for raw in doc.get("payment_method"):
            if raw.method=="Points":
                if raw.otp==None and raw.points==None:
                    frappe.throw(_("You have not entered otp and points "))
                if raw.otp==None:
                    frappe.throw(_("You have not entered otp"))
                if raw.points==None:
                    frappe.throw(_("You have not entered points "))
                if raw.otp!=doc.otp:
                        frappe.throw(_("Please enter correct otp "))
def payment_check(doc):
    total=0
    for raw in doc.get("payment_method"):
        if raw.method=="COD" or raw.method=="CC":
            total+=int(raw.amount)
        else:
            total+=int(raw.points)
    if total< doc.grand_total:
        return None
