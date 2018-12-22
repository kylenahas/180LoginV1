import tkinter as tk
from tkinter import *
from enum import Enum

import config
from dbManage import *
from forms import FormHelp
from barcodeGen import *


class EMWContext(Enum):
    NewMember = 1
    UpdateMember = 2


class EditMemberWindow:
    def __init__(self, master=None, context=EMWContext.NewMember):

        # nmw == New Member Window
        self.emw = Toplevel()
        self.context = context
        self.populate()
        self.center()
        if self.context == EMWContext.NewMember:
            self.emw.title("New Member")
        elif self.context == EMWContext.UpdateMember:
            self.emw.title("Update Member")

            self.punches_remaining_hide()
            self.expiration_date_hide()

    def center(self):
        self.emw.update_idletasks()
        width = self.emw.winfo_width()
        height = self.emw.winfo_height()
        x = (self.emw.winfo_screenwidth() // 2) - (width // 2)
        y = (self.emw.winfo_screenheight() // 2) - (height // 2)
        self.emw.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def populate(self):

        if self.context == EMWContext.NewMember:
            forms = {"name_first": "First Name",
                     "name_last": "Last Name",
                     "email": "Email",
                     "phone": "Phone Number",
                     "dob": "Date of Birth",
                     "member_type": "Member Type"}

            if config.member_link_enabled:
                forms["member_opts"] = "Link Member"

            self.entry_data_dict = FormHelp.make_forms(self.emw, forms)
            self.entry_data = self.entry_data_dict["entries"]

            if config.member_link_enabled:
                self.link_member_init()

            Button(self.emw, text="Add Member", command=self.enter_to_db).grid(pady=(15, 0))
            self.entry_data["name_first"].focus()
        elif self.context == EMWContext.UpdateMember:
            forms = {"id": "Member ID",
                     "name_first": "First Name",
                     "name_last": "Last Name",
                     "email": "Email",
                     "phone": "Phone Number",
                     "dob": "Date of Birth",
                     "member_type": "Member Type",
                     "expiration_punches": "Punches Remaining",
                     "expiration_date": "Expiration Date"}

            if config.member_link_enabled:
                forms["member_opts"] = "Link Member"

            self.entry_data_dict = FormHelp.make_forms(self.emw, forms)
            self.entry_data = self.entry_data_dict["entries"]

            # Disable all entries but ID if updating member
            for form in self.entry_data.keys():
                if form == "id":
                    self.entry_data[form].focus()
                    self.entry_data[form].bind('<Return>', (lambda _: self.retrieve_member(self.entry_data[form])))
                elif form == "member_type":
                    self.entry_data[form].config(state=DISABLED)
                # elif form == "member_type_radios":
                #     for radio in self.entry_data[form]:
                #         radio.config(state=DISABLED)
                elif form == "dob_arr" or form == "exp_date_arr":
                    for spinbox in self.entry_data[form]:
                        spinbox.config(state=DISABLED)
                elif form == "member_opts_vars":
                    for elements in self.entry_data[form]:
                        elements.config(state=DISABLED)
                elif form == "member_opts":
                    pass
                else:
                    self.entry_data[form].config(state=DISABLED)
            self.add_credits_button = Button(self.emw, text="Add credits", command=self.add_credits,
                                             state=DISABLED)
            self.add_credits_button.grid(column=0, pady=10)

            if config.sign_offs_enabled:
                self.edit_member_sign_offs = Button(self.emw, text="Edit Member Sign Offs", command=self.edit_sign_offs,
                                                    state=DISABLED)
                self.edit_member_sign_offs.grid(column=0)

            self.entry_data["member_type"].bind("<<ComboboxSelected>>", self.switch_expiration_type)

            Button(self.emw, text="Update Member", command=self.enter_to_db).grid(column=0, pady=20)

    def retrieve_member(self, event):
        try:
            member_info = config.appDB.retrieve_member(int(self.entry_data["id"].get()))

            for form in self.entry_data.keys():
                if form == "id":
                    self.entry_data[form].config(state=DISABLED)
                elif form == "member_type":
                    self.entry_data[form].config(state="readonly")
                    # member_types_inv = {v: k for k, v in config.member_types.items()}  # https://stackoverflow.com/a/483833
                    self.entry_data[form].set(config.member_types.get(member_info[form]))
                elif form == "member_type_radios":
                    for radio in self.entry_data[form]:
                        radio.config(state=NORMAL)
                elif form == "dob_arr" or form == "exp_date_arr":
                    for spinbox in self.entry_data[form]:
                        spinbox.config(state=NORMAL)
                elif form == "member_opts_vars":
                    # for elements in self.entry_data[form]:
                    self.entry_data[form][1].config(state=NORMAL)
                    self.entry_data[form][2].config(state=NORMAL)
                    self.link_member_init()
                    self.link_member_fill(link=member_info.get("link", None))
                elif form == "member_opts":
                    pass
                # elif form == "expiration_date":
                #     # self.expiration_date_init()
                #     pass
                else:
                    self.entry_data[form].config(state=NORMAL)
                    self.entry_data[form].delete(0, END)
                    self.entry_data[form].insert(0, member_info.get(form, ""))

            self.sync_dob()
            # self.sync_exp_date()

            self.add_credits_button.config(state=NORMAL)
            self.switch_expiration_type(member_type=None)

            if config.sign_offs_enabled:
                self.edit_member_sign_offs.config(state=NORMAL)

        except ValueError:
            messagebox.showwarning(title="Problem retrieving member data!", message="Member not found!")
            self.emw.focus_force()
            self.entry_data["id"].delete(0, END)
            self.entry_data["id"].focus()

    def enter_to_db(self):
        fh = FormHelp()
        self.sync_dob()
        # printed_vals = fh.print_values(entries=self.entry_data)
        try:
            if self.validate_entries():
                print("Form ok!")
                member_type = self.entry_data["member_type"].get()
                member_types_inv = {v: k for k, v in config.member_types.items()}  # https://stackoverflow.com/a/483833
                member_type_str = member_types_inv.get(member_type)
                try:
                    if self.context == EMWContext.NewMember:
                        new_member = config.appDB.add_member(
                            first_name=self.entry_data["name_first"].get().capitalize(),
                            last_name=self.entry_data["name_last"].get().capitalize(),
                            email=self.entry_data["email"].get(),
                            phone=self.entry_data["phone"].get(),
                            birthdate=self.entry_data["dob"].get(),
                            member_type_str=member_type_str,
                            link=self.link_member_generate())
                        nm_success_str = "Successfully created member: " + new_member["name_first"] + " " + new_member[
                            "name_last"]
                        messagebox.showinfo(title="New Member Status", message=nm_success_str)

                        barcode = Barcoder()

                        # barcode.create_barcode(new_member["id"])
                        member_id = new_member["id"]
                        name_str = new_member["name_first"] + " " + new_member["name_last"]
                        file = new_member["name_first"].lower() + "." + new_member["name_last"].lower()
                        # member_type = new_member["member_type"].capitalize()
                        barcode.create_sticker_image(member_id, name_str=name_str, member_type_str=member_type,
                                                     fn=file)

                        barcode.open_barcode(fn="exported_stickers/" + file + ".png")

                    elif self.context == EMWContext.UpdateMember:
                        # if member_type == "monthly" or member_type == "annual" \
                        #         or member_type == "student" or member_type == "student_annual":
                        #     self.sync_exp_date()
                        updated_member = config.appDB.update_member(member_id=int(self.entry_data["id"].get()),
                                                                    first_name=self.entry_data[
                                                                        "name_first"].get().capitalize(),
                                                                    last_name=self.entry_data[
                                                                        "name_last"].get().capitalize(),
                                                                    email=self.entry_data["email"].get(),
                                                                    phone=self.entry_data["phone"].get(),
                                                                    birthdate=self.entry_data["dob"].get(),
                                                                    member_type_str=member_type_str,
                                                                    expiration_punches=int(
                                                                        self.entry_data["expiration_punches"].get()),
                                                                    expiration_date=self.entry_data[
                                                                        "expiration_date"].get(),
                                                                    link=self.link_member_generate())

                        nm_success_str = "Successfully updated member: " + updated_member["name_first"] + " " + \
                                         updated_member["name_last"]
                        messagebox.showinfo(title="Update Member Status", message=nm_success_str)

                    self.emw.destroy()
                except Exception as e:
                    messagebox.showwarning(title="Problem adding member!", message="An exception occured:\n" + str(e))
            else:
                if self.context == EMWContext.NewMember:
                    messagebox.showwarning(title="Problem adding member!", message="Data not completely filled")
                elif self.context == EMWContext.UpdateMember:
                    messagebox.showwarning(title="Problem updating member!", message="Data not completely filled")

                self.emw.focus_force()
        except Exception as e:
            messagebox.showwarning(title="Problem adding member!", message="An exception occured:\n" + str(e))
            self.emw.focus_force()

    def edit_sign_offs(self):
        signOffs = memberSignOffs(member_id=int(self.entry_data["id"].get()))
        signOffs.editWindow()

    def add_credits(self):
        member_type = self.entry_data["member_type"].get()
        # print("Member type changed to: " + member_type)
        if member_type == config.member_types["monthly"] or member_type == config.member_types["student"]:
            self.sync_exp_date(add_credit_days=31)

        elif member_type == config.member_types["annual"] or member_type == config.member_types["student_annual"]:
            self.sync_exp_date(add_credit_days=365)


        elif member_type == config.member_types["punchcard"]:
            self.add_10_punches()

    def add_10_punches(self):
        punches = int(self.entry_data["expiration_punches"].get()) + 10
        self.entry_data["expiration_punches"].delete(0, END)
        self.entry_data["expiration_punches"].insert(0, punches)

        print("10 punches added!")

    def sync_dob(self):
        if self.entry_data["dob"].get() == "yyyy-mm-dd":
            year = self.entry_data["dob_arr"][0].get()
            month = self.entry_data["dob_arr"][1].get()
            day = self.entry_data["dob_arr"][2].get()

            if int(month) < 10:
                month = "0" + str(month)
            if int(day) < 10:
                day = "0" + str(day)

            dob_str = str(year) + "-" + str(month) + "-" + str(day)

            self.entry_data["dob"].delete(0, END)
            self.entry_data["dob"].insert(0, dob_str)

            return dob_str
        else:
            dob = self.entry_data["dob"].get().split("-")

            # Year Entry
            self.entry_data["dob_arr"][0].delete(0, END)
            self.entry_data["dob_arr"][0].insert(0, dob[0])

            # Month Entry
            self.entry_data["dob_arr"][1].delete(0, END)
            self.entry_data["dob_arr"][1].insert(0, dob[1])

            # Day Entry
            self.entry_data["dob_arr"][2].delete(0, END)
            self.entry_data["dob_arr"][2].insert(0, dob[2])

    def sync_exp_date(self, add_credit_days=None, spinbox_change=False):
        exp_date_str = self.entry_data["expiration_date"].get()
        member_type = self.entry_data["member_type"].get()

        if exp_date_str == "-1":
            exp_date = datetime.now()
            if member_type == config.member_types["monthly"] or member_type == config.member_types["student"]:
                add_credit_days = 31
            elif member_type == config.member_types["annual"] or member_type == config.member_types["student_annual"]:
                add_credit_days = 365



        else:
            exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d %H:%M:%S.%f')

            if (datetime.now() > exp_date) and not spinbox_change:
                exp_date = datetime.now()
                if member_type == config.member_types["monthly"] or member_type == config.member_types["student"]:
                    add_credit_days = 31
                    credit_str = "1 month"
                elif member_type == config.member_types["annual"] or member_type == config.member_types[
                    "student_annual"]:
                    add_credit_days = 365
                    credit_str = "1 year"
                messagebox.showinfo(title="Membership Renewed",
                                    message="Membership was expired.\n\nAutomatically added "
                                            + credit_str + " to member's account.")
                self.emw.focus_force()

        if spinbox_change:
            # exp_date = datetime.now()
            year = int(self.entry_data["exp_date_arr"][0].get())
            month = int(self.entry_data["exp_date_arr"][1].get())
            day = int(self.entry_data["exp_date_arr"][2].get())

            ret = True
            try:
                exp_date = datetime(year=year, month=month, day=day, microsecond=1)
                print(exp_date)
            except:
                ret = False

            # exp_date.replace(year=year)
            # exp_date.replace(month=month)
            # exp_date.replace(day=day)

        if add_credit_days is not None:
            exp_date += timedelta(days=add_credit_days)

        # Year Entry
        self.entry_data["exp_date_arr"][0].delete(0, END)
        self.entry_data["exp_date_arr"][0].insert(0, str(exp_date.year))

        # Month Entry
        self.entry_data["exp_date_arr"][1].delete(0, END)
        self.entry_data["exp_date_arr"][1].insert(0, str(exp_date.month))

        # Day Entry
        self.entry_data["exp_date_arr"][2].delete(0, END)
        self.entry_data["exp_date_arr"][2].insert(0, str(exp_date.day))

        # Finally, sync text box to date shown in box
        self.entry_data["expiration_date"].delete(0, END)
        self.entry_data["expiration_date"].insert(0, str(exp_date))

        if spinbox_change:
            return ret

    def validate_entries(self):
        ret = True
        self.sync_dob()
        for field_name in self.entry_data.keys():
            if field_name == "member_type_radios":
                pass
            elif field_name == "dob_arr":
                pass
            elif field_name == "exp_date_arr":
                pass
            elif field_name == "member_opts" or field_name == "member_opts_vars":
                if not self.link_member_validate():
                    ret = False
                pass
            else:
                if self.entry_data[field_name].get() == "":
                    ret = False
        return ret

    # TODO: Make link member a class

    def link_member_init(self):
        _vars = self.entry_data["member_opts_vars"]
        _vars[1].config(command=lambda: self.link_member_toggle(opt="addon"))
        _vars[2].config(command=lambda: self.link_member_toggle(opt="org"))

    def link_member_toggle(self, opt):
        _vars = self.entry_data["member_opts"]
        form = self.entry_data["member_opts_vars"]
        if opt == "addon":
            if (_vars[1].get() == "1"):
                _vars[2].set("0")
                form[0].config(state=NORMAL)
                form[0].focus_force()
            elif (_vars[2].get() == "1"):
                pass
            else:
                form[0].delete(0, END)
                form[0].insert(0, "")
                form[0].config(state=DISABLED)
        elif opt == "org":
            if (_vars[2].get() == "1"):
                _vars[1].set("0")
                form[0].config(state=NORMAL)
                form[0].focus_force()
            elif (_vars[1].get() == "1"):
                pass
            else:
                form[0].delete(0, END)
                form[0].insert(0, "")
                form[0].config(state=DISABLED)

    def link_member_fill(self, link):
        _vars = self.entry_data["member_opts"]
        form = self.entry_data["member_opts_vars"]
        if link is None:
            return
        else:
            if link.get("link_opt", "") == "addon":
                _vars[1].set("1")
            elif link.get("link_opt", "") == "org":
                _vars[2].set("1")
            form[0].config(state=NORMAL)
            form[0].delete(0, END)
            form[0].insert(0, link.get("link_id", ""))

    def link_member_generate(self):
        _vars = self.entry_data["member_opts"]
        form = self.entry_data["member_opts_vars"]

        if _vars[1].get() == "0" and _vars[2].get() == "0":
            return None
        else:
            link = {"link_id": _vars[0].get()}
            if _vars[1].get() == "1":
                link["link_opt"] = "addon"
            elif _vars[2].get() == "1":
                link["link_opt"] = "org"
            return link

    def link_member_validate(self):
        _vars = self.entry_data["member_opts"]
        if _vars[1].get() == "0" and _vars[2].get() == "0":
            return True
        else:
            try:
                link_id = int(_vars[0].get())
            except Exception:
                raise ValueError("The linked user ID could not be found in the database\n\n"
                                 "(HINT: Scan the card of the member you are trying to link to)")
            member_query = Query()
            if config.appDB.membersDB.contains(member_query.id == link_id):
                print("Valid Linked ID")
                return True
            else:
                raise ValueError("The linked user ID could not be found in the database\n\n"
                                 "(HINT: Scan the card of the member you are trying to link to)")

    def switch_expiration_type(self, member_type=None):
        # if member_type is NONE:
        member_type = self.entry_data["member_type"].get()
        # print("Member type changed to: " + member_type)
        if member_type == config.member_types["monthly"] or member_type == config.member_types["student"]:
            # Show expiration date and change button to be "Add Month"
            self.punches_remaining_hide()
            self.expiration_date_show()

            self.add_credits_button.grid()
            self.add_credits_button.config(text="Add 1 Month")


        elif member_type == config.member_types["annual"] or member_type == config.member_types["student_annual"]:
            # Show expiration date and change button to be "Add Year"

            self.punches_remaining_hide()
            self.expiration_date_show()

            self.add_credits_button.grid()
            self.add_credits_button.config(text="Add 1 Year")


        elif member_type == config.member_types["punchcard"]:
            # Show punches remainging, button adds 10 punches

            self.expiration_date_hide()
            self.punches_remaining_show()

            self.add_credits_button.grid()
            self.add_credits_button.config(text="Add 10 Punches")


        else:
            self.expiration_date_hide()
            self.punches_remaining_hide()
            self.add_credits_button.grid_remove()

    def expiration_date_init(self):
        for spinbox in self.entry_data["exp_date_arr"]:
            spinbox.config(validate="all", validatecommand=lambda: self.sync_exp_date(spinbox_change=True),
                           command=lambda: self.sync_exp_date(spinbox_change=True))

    def expiration_date_hide(self):
        for spinbox in self.entry_data["exp_date_arr"]:
            spinbox.grid_remove()
        for labels in self.entry_data_dict["labels"]["exp_date_arr"]:
            labels.grid_remove()
        self.entry_data_dict["labels"]["expiration_date"].grid_remove()

    def expiration_date_show(self):
        for spinbox in self.entry_data["exp_date_arr"]:
            spinbox.grid()
        for labels in self.entry_data_dict["labels"]["exp_date_arr"]:
            labels.grid()
        self.entry_data_dict["labels"]["expiration_date"].grid()
        self.sync_exp_date()
        self.expiration_date_init()

    def punches_remaining_hide(self):
        self.entry_data["expiration_punches"].grid_remove()
        self.entry_data_dict["labels"]["expiration_punches"].grid_remove()

    def punches_remaining_show(self):
        self.entry_data["expiration_punches"].grid()
        self.entry_data_dict["labels"]["expiration_punches"].grid()


class memberSignOffs:
    def __init__(self, member_id):
        if member_id is None:
            raise ValueError("Sign Offs must be passed a member ID")
        else:
            self.mid = int(member_id)

    def editWindow(self):
        self.root = Toplevel()
        self.populate_list()
        self.center(self.root)

    def center(self, root):
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def populate_list(self):
        form = StringVar()
        row_number = 0
        Label(self.root, text="Member is signed off on:").grid(row=0, column=0, padx=15, pady=10, sticky=W)

        # sign_off_list = {  "woodshop": "Woodshop",
        #                    "shopbot": "ShopBot",
        #                    "laser": "Laser Cutter",
        #                    "3dprinter": "3D Printer",
        #                    "machineshop": "Machine Shop",
        #                    "welding": "Welding"}

        self.checks = []
        i = 0
        db_checks = config.appDB.get_member_sign_offs(member_id=self.mid)
        for activity in config.sign_off_list.keys():
            bv = BooleanVar()
            bv.set(db_checks.get(activity, False))
            cb = Checkbutton(self.root, text=config.sign_off_list[activity], variable=bv)
            # if i % 6 == 0 and i != 0:
            row_number += 1
            cb.grid(row=row_number, column=0, columnspan=2, sticky=W)
            self.checks.append(bv)
            # i += 2
        save = Button(self.root, text="Save Member Sign-Offs", command=self.save_clicked)
        save.grid(column=0, pady=10)

    def save_clicked(self):
        local_checks = self.generate_dict_from_edit_window()
        config.appDB.set_member_sign_offs(member_id=self.mid, sign_offs=local_checks)
        self.root.destroy()


    def generate_dict_from_edit_window(self):
        i=0
        sign_offs = {}
        for activity in config.sign_off_list.keys():
            sign_offs[activity] = self.checks[i].get()
            i += 1

        return sign_offs


    def printSignOffs(member_id):
        checks = config.appDB.get_member_sign_offs(member_id=member_id)
        retStr = ""
        for activity in config.sign_off_list.keys():
            if checks[activity]:
                retStr += "[X] "
            else:
                retStr += "[  ] "
            retStr += config.sign_off_list[activity] + "\n"
        return retStr
