from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from frappe.utils.background_jobs import enqueue
import json

@frappe.whitelist(allow_guest=True)
def generate_attendance_long(data= None):
	attendance = frappe.request.data
	try:
		enqueue("ikit_biometric_connector.employee_attendance.generate_attendance", attendance=attendance, queue='long', timeout=4500)
		return "Queued"
	except Exception as e:
		error_message = f"""{frappe.get_traceback()}\n{attendance}\n{e}"""
		frappe.log_error(error_message, "Error Exception Queque")

@frappe.whitelist(allow_guest=True)
def generate_attendance(attendance = None):
	try:
		attendance = json.loads(attendance).get("data")
		for a  in attendance:
			a = str(a).split()
			biometric, date, time, in_out= str(a[1]), a[3], a[4], cint(a[6].replace(")", ""))
			date_time = f"""{date} {time}"""
			emp = frappe.db.get_value("Employee", {"status": "Active", "attendance_device_id": biometric}, "name")
			if emp:
				att = frappe.db.get_value("Employee Checkin", {"employee": emp, "time": date_time}, "name")
				if not att:
					try:
						new_att = frappe.new_doc("Employee Checkin")
						new_att.employee = emp
						new_att.time = date_time
						new_att.log_type = "OUT" if in_out else "IN"
						new_att.flags.ignore_permissions=True
						new_att.save()
					except Exception as e:
						error_message = f"""{frappe.get_traceback()}\n{a}\n{e}"""
						frappe.log_error(error_message, "Checkin Creation Error from Mobile App")
	except Exception as e:
		error_message = f"""{frappe.get_traceback()}\n{attendance}\n{e}"""
		frappe.log_error(error_message, "Generate Attendance Error from Mobile App")