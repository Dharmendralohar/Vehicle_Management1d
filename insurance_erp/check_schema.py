import frappe

def check_schema():
    meta = frappe.get_meta("Number Card")
    for f in meta.fields:
        print(f"{f.fieldname}: {f.label}")

if __name__ == "__main__":
    check_schema()
