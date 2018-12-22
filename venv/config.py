from dbManage import LoginDatabase

appDB = LoginDatabase()

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

sign_offs_enabled = False
member_link_enabled = True

