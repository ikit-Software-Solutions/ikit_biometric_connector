from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr
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
		frappe.log_error("Error Exception Queque", error_message)


def clean_string_value(val):
	if val:
		return cstr(val).replace(",", "").replace("(", "").replace(")", "").strip()
	return val

@frappe.whitelist(allow_guest=True)
def generate_attendance(attendance = None):
	try:
		attendance = json.loads(attendance).get("data")
		frappe.log_error("Attendance Data From app", cstr(attendance))
		for a  in attendance:
			a = str(a).split()
			biometric, date, time, in_out_1, in_out_2 = str(a[1]), a[3], a[4], cint(clean_string_value(a[5])), cint(clean_string_value(a[6]))
			date_time = f"""{date} {time}"""
			emp = frappe.db.get_value("Employee", {"status": "Active", "attendance_device_id": biometric}, "name")
			if emp:
				att = frappe.db.get_value("Employee Checkin", {"employee": emp, "time": date_time}, "name")
				if not att:
					try:
						new_att = frappe.new_doc("Employee Checkin")
						new_att.employee = emp
						new_att.time = date_time
						log_type =  None
						if in_out_1 == 0 and in_out_2 == 0:
							log_type = "IN" 
						elif in_out_1 == 0 and in_out_2 == 1:
							log_type = "OUT" 
						new_att.log_type = log_type
						new_att.flags.ignore_permissions=True
						new_att.save()
					except Exception as e:
						error_message = f"""{frappe.get_traceback()}\n{a}\n{e}"""
						frappe.log_error("Checkin Creation Error from Mobile App", error_message)
	except Exception as e:
		error_message = f"""{frappe.get_traceback()}\n{attendance}\n{e}"""
		frappe.log_error("Generate Attendance Error from Mobile App", error_message)