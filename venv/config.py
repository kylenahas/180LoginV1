from dbManage import LoginDatabase

# Should end with / or be None for current directory
# db_dir = "./"
db_dir = None

appDB = LoginDatabase(db_dir=db_dir)

member_types = { "punchcard": "Punchcard",
                 "monthly": "Monthly",
                 "annual": "Annual",
                 "student": "Student - Monthly",
                 "student_annual": "Student - Annual",
                 "trial": "7 Day Trial",
                 "organization": "Organization",
                 "volunteer": "Volunteer"}

sign_off_list = {"woodshop": "Woodshop",
                 "shopbot": "ShopBot",
                 "laser": "Laser Cutter",
                 "3dprinter": "3D Printer",
                 "machineshop": "Machine Shop",
                 "sewing": "Sewing",
                 "welding": "Welding"}

sign_offs_enabled = True
member_link_enabled = True
allow_multiple_scans_a_day = False


zebra_printer_name = "Zebra_Technologies_ZTC_ZD410-203dpi_ZPL"
zebra_print_enabled = True

log_errors_to_file = True
