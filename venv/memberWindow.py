import tkinter as tk
from tkinter import *
from enum import Enum

import config
from dbManage import *
from forms import FormHelp

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



    def center(self):
        self.emw.update_idletasks()
        width = self.emw.winfo_width()
        height = self.emw.winfo_height()
        x = (self.emw.winfo_screenwidth() // 2) - (width // 2)
        y = (self.emw.winfo_screenheight() // 2) - (height // 2)
        self.emw.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def populate(self):

        if self.context == EMWContext.NewMember:
            self.entry_data = FormHelp.make_forms(self.emw, {"name_first": "First Name",
                                                             "name_last": "Last Name",
                                                             "email": "Email",
                                                             "phone": "Phone Number",
                                                             "dob": "Date of Birth",
                                                             "member_type": "Member Type",
                                                             "member_opts": "Link Member"})
            self.link_member_init()
            Button(self.emw, text="Add Member", command=self.enter_to_db).grid(pady=(15, 0))
            self.entry_data["name_first"].focus()
        elif self.context == EMWContext.UpdateMember:
            self.entry_data = FormHelp.make_forms(self.emw, {   "id": "Member ID",
                                                                "name_first": "First Name",
                                                                "name_last": "Last Name",
                                                                "email": "Email",
                                                                "phone": "Phone Number",
                                                                "dob": "Date of Birth",
                                                                "member_type": "Member Type",
                                                                "expiration_punches": "Punches Remaining"})
            # Disable all entries but ID if updating member
            for form in self.entry_data.keys():
                if form == "id":
                    self.entry_data[form].focus()
                    self.entry_data[form].bind('<Return>', (lambda _: self.retrieve_member(self.entry_data[form])))
                elif form == "member_type":
                    pass
                elif form == "member_type_radios":
                    for radio in self.entry_data[form]:
                        radio.config(state=DISABLED)
                elif form == "dob_arr":
                    for spinbox in self.entry_data[form]:
                        spinbox.config(state=DISABLED)
                else:
                    self.entry_data[form].config(state=DISABLED)
            self.add_punches_button = Button(self.emw, text="Add 10 Punches", command=self.add_10_punches, state=DISABLED)
            self.add_punches_button.grid(column=0, pady=10)
            self.edit_member_sign_offs = Button(self.emw, text="Edit Member Sign Offs", command=self.edit_sign_offs, state=DISABLED)
            self.edit_member_sign_offs.grid(column=0)

            Button(self.emw, text="Update Member", command=self.enter_to_db).grid(column=0, pady=20)

    def retrieve_member(self, event):
        try:
            member_info = config.appDB.retrieve_member(int(self.entry_data["id"].get()))

            for form in self.entry_data.keys():
                if form == "id":
                    self.entry_data[form].config(state=DISABLED)
                elif form == "member_type":
                    self.entry_data[form].set(member_info[form])
                elif form == "member_type_radios":
                    for radio in self.entry_data[form]:
                        radio.config(state=NORMAL)
                elif form == "dob_arr":
                    for spinbox in self.entry_data[form]:
                        spinbox.config(state=NORMAL)
                else:
                    self.entry_data[form].config(state=NORMAL)
                    self.entry_data[form].delete(0, END)
                    self.entry_data[form].insert(0, member_info[form])

            self.sync_dob()

            self.add_punches_button.config(state=NORMAL)
            self.edit_member_sign_offs.config(state=NORMAL)


        except ValueError:
            messagebox.showwarning(title="Problem retrieving member data!", message="Member not found!")
            self.emw.focus_force()
            self.entry_data["id"].delete(0, END)
            self.entry_data["id"].focus()


    def enter_to_db(self):
        fh=FormHelp()
        self.sync_dob()
        printed_vals = fh.print_values(entries=self.entry_data)
        if self.validate_entries():
            print("Form ok!")
            try:
                if self.context == EMWContext.NewMember:
                    new_member = config.appDB.add_member(first_name=self.entry_data["name_first"].get().capitalize(),
                                                  last_name=self.entry_data["name_last"].get().capitalize(),
                                                  email=self.entry_data["email"].get(),
                                                  phone=self.entry_data["phone"].get(),
                                                  birthdate=self.entry_data["dob"].get(),
                                                  member_type_str=self.entry_data["member_type"].get())
                    nm_success_str = "Successfully created member: " + new_member["name_first"] + " " + new_member[
                        "name_last"]
                    messagebox.showinfo(title="New Member Status", message=nm_success_str)

                    barcode = Barcoder()

                    # barcode.create_barcode(new_member["id"])
                    member_id = new_member["id"]
                    name_str = new_member["name_first"] + " " + new_member["name_last"]
                    file = new_member["name_first"].lower() + "." + new_member["name_last"].lower()
                    member_type = new_member["member_type"].capitalize()
                    barcode.create_sticker_image(member_id, name_str=name_str, member_type_str=member_type, fn=file)

                    barcode.open_barcode(fn="exported_stickers/"+file+".png")

                elif self.context == EMWContext.UpdateMember:
                    updated_member = config.appDB.update_member(member_id=int(self.entry_data["id"].get()),
                                                         first_name=self.entry_data["name_first"].get().capitalize(),
                                                         last_name=self.entry_data["name_last"].get().capitalize(),
                                                         email=self.entry_data["email"].get(),
                                                         phone=self.entry_data["phone"].get(),
                                                         birthdate=self.entry_data["dob"].get(),
                                                         member_type_str=self.entry_data["member_type"].get(),
                                                         expiration_punches=int(self.entry_data["expiration_punches"].get()))
                    nm_success_str = "Successfully updated member: " + updated_member["name_first"] + " " + updated_member["name_last"]
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

    def edit_sign_offs(self):
        signOffs = memberSignOffs(member_id=self.entry_data["id"].get())
        signOffs.editWindow()

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

    def validate_entries(self):
        ret = True
        self.sync_dob()
        for field_name in self.entry_data.keys():
            if field_name == "member_type_radios":
                pass
            elif field_name == "dob_arr":
                pass
            elif field_name == "member_opts" or field_name == "member_opts_vars":
                pass
            else:
                if self.entry_data[field_name].get() == "":
                    ret = False
        return ret

    def link_member_init(self):
        _vars = self.entry_data["member_opts_vars"]
        _vars[1].config(command=lambda: self.link_member_toggle(opt="addon"))
        _vars[2].config(command=lambda: self.link_member_toggle(opt="org"))

    def link_member_toggle(self, opt):
        _vars = self.entry_data["member_opts"]
        form = self.entry_data["member_opts_vars"]
        if opt == "addon":
            if(_vars[1].get() == "1"):
                _vars[2].set("0")
                form[0].config(state=NORMAL)
            elif(_vars[2].get() == "1"):
                pass
            else:
                form[0].config(state=DISABLED)
        elif opt == "org":
            if(_vars[2].get() == "1"):
                _vars[1].set("0")
                form[0].config(state=NORMAL)
            elif(_vars[1].get() == "1"):
                pass
            else:
                form[0].config(state=DISABLED)


class memberSignOffs:
    def __init__(self, member_id=None):
        if member_id is None:
            raise ValueError("Sign Offs must be passed a member ID")
        else:
            self.mid = member_id


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
        Label(self.root, text="Member is signed off on:").grid(row=0, column=0, pady=10, sticky=W)
        sign_off_list = ["Woodshop",
                         "ShopBot",
                         "Laser Cutter",
                         "3D Printer",
                         "Machine Shop",
                         "Welding",]
        checks = []
        i = 0
        for text in sign_off_list:
            cb = Checkbutton(self.root, text=text)
            # if i % 6 == 0 and i != 0:
            row_number += 1
            cb.grid(row=row_number, column=0, columnspan=2, sticky=W)
            checks.append(cb)
            # i += 2
        Button(self.root, text="Save Member Sign-Offs").grid(column=0, pady=10)
        
    def printSignOffs(self):
        retStr = "[X] Wood shop\n[X] Laser Cutter\n[  ] 3D Printer\n[  ] Machine Shop"
        return retStr



