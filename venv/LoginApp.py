import tkinter as tk
from tkinter import *
from tkinter import messagebox, StringVar, ttk
from tkcalendar import Calendar, DateEntry
from enum import Enum

import pprint

from dbManage import *
from barcodeGen import *

class EMWContext(Enum):
    NewMember = 1
    UpdateMember = 2


class Splash(tk.Frame):
    # global scanner_input_sv

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_splash()

    def create_splash(self):
        self.scannerLabelText = tk.Label(text='Scan Member Card:')
        self.scannerLabelText.pack(pady=10)
        self.scannerLabelText.pack(side='top', expand=0)

        global scanner_input_sv  # FIXME: I'd rather not have to use a global here.
        scanner_input_sv = StringVar()

        self.scannerInput = tk.Entry(textvariable=scanner_input_sv)
        self.scannerInput.pack(side='top', expand=0)
        self.scannerInput.focus_set()

        # e.bind('<Return>', (lambda _: callback(e)))  # https://stackoverflow.com/a/39059073
        self.scannerInput.bind('<Return>', (lambda _: self.login_member(self.scannerInput)))

        tk.Label(text="-or-").pack(pady=(30, 0), side='top', expand=0)

        tk.Button(command=self.add_new_member_pushed, text="Add New Member").pack(side='left', expand=1, padx=15, pady=10)

        tk.Button(command=self.update_member_pushed, text="Update Member").pack(side='right', expand=1, padx=15, pady=10)

    def clear_window(self):  # https://stackoverflow.com/a/44955479
        list = root.grid_slaves()
        for l in list:
            l.destroy()

    def center(self):
        # https://stackoverflow.com/a/10018670
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        splashWindow.master.minsize(width=width, height=height)
        splashWindow.master.maxsize(width=width, height=height)

    def add_new_member_pushed(self):
        # NewMemberWindow()
        EditMemberWindow(context=EMWContext.NewMember)

    def update_member_pushed(self):
        # UpdateMemberWindow()
        EditMemberWindow(context=EMWContext.UpdateMember)


    def login_member(self, event):
        try:
            member_id = int(self.scannerInput.get())
            logged_member = my_db.log_member(member_id)
            info_str = "Member: " + logged_member["name_first"] + " " + logged_member["name_last"] + " logged in!\n\n"
            if my_db.retrieve_member(member_id)["member_type"] == "punchcard":
                info_str += "Punches left: " + str(logged_member["remaining_punches"])
            messagebox.showinfo(title="Logging in:", message=info_str)
        except ValueError:
            messagebox.showwarning(title="Problem logging in member!", message="Member not found!")
        except RuntimeError:
            messagebox.showwarning(title="Problem logging in member!", message="Member has used all their punches!\n\nRefill punches before entry!")
        finally:
            self.scannerInput.delete(0, END)
            super().focus_force()
            self.scannerInput.focus()


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
        style = ttk.Style(self.emw)
        style.theme_use('clam')



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
                                                             "member_type": "Member Type"})
            Button(self.emw, text="Add Member", command=self.enter_to_db).pack(side=BOTTOM, pady=10)
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
                else:
                    self.entry_data[form].config(state=DISABLED)
            self.add_punches_button = Button(self.emw, text="Add 10 Punches", command=self.add_10_punches, state=DISABLED)
            self.add_punches_button.pack(side=LEFT, pady=10, padx=20)
            Button(self.emw, text="Update Member", command=self.enter_to_db).pack(side=RIGHT, pady=10, padx=20)

    def retrieve_member(self, event):
        try:
            member_info = my_db.retrieve_member(int(self.entry_data["id"].get()))

            for form in self.entry_data.keys():
                if form == "id":
                    self.entry_data[form].config(state=DISABLED)
                elif form == "member_type":
                    self.entry_data[form].set(member_info[form])
                elif form == "member_type_radios":
                    for radio in self.entry_data[form]:
                        radio.config(state=NORMAL)
                else:
                    self.entry_data[form].config(state=NORMAL)
                    self.entry_data[form].delete(0, END)
                    self.entry_data[form].insert(0, member_info[form])

            self.add_punches_button.config(state=NORMAL)


        except ValueError:
            messagebox.showwarning(title="Problem retrieving member data!", message="Member not found!")
            self.nmw.focus_force()
            self.entry_data["id"].delete(0, END)
            self.entry_data["id"].focus()


    def enter_to_db(self):
        fh=FormHelp()
        printed_vals = fh.print_values(entries=self.entry_data)
        if self.validate_entries():
            print("Form ok!")
            try:
                if self.context == EMWContext.NewMember:
                    new_member = my_db.add_member(first_name=self.entry_data["name_first"].get().capitalize(),
                                                  last_name=self.entry_data["name_last"].get().capitalize(),
                                                  email=self.entry_data["email"].get(),
                                                  phone=self.entry_data["phone"].get(),
                                                  birthdate=self.entry_data["dob"].get(),
                                                  member_type_str=self.entry_data["member_type"].get())
                    nm_success_str = "Successfully created member: " + new_member["name_first"] + " " + new_member[
                        "name_last"]
                    messagebox.showinfo(title="New Member Status", message=nm_success_str)

                    barcode = Barcoder()

                    barcode.create_barcode(new_member["id"])
                    barcode.open_barcode()

                elif self.context == EMWContext.UpdateMember:
                    updated_member = my_db.update_member(member_id=int(self.entry_data["id"].get()),
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
            except ValueError:  # add_member() does not currently throw any exceptions.
                pass
        else:
            if self.context == EMWContext.NewMember:
                messagebox.showwarning(title="Problem adding member!", message="Data not completely filled")
            elif self.context == EMWContext.UpdateMember:
                messagebox.showwarning(title="Problem updating member!", message="Data not completely filled")

            self.emw.focus_force()

    def add_10_punches(self):
        punches = int(self.entry_data["expiration_punches"].get()) + 10
        self.entry_data["expiration_punches"].delete(0, END)
        self.entry_data["expiration_punches"].insert(0, punches)


        print("10 punches added!")



    def validate_entries(self):
        ret = True
        for field_name in self.entry_data.keys():
            if field_name == "member_type_radios":
                pass
            else:
                if self.entry_data[field_name].get() == "":
                    ret = False
        return ret


class FormHelp:
    def print_values(self, entries):
        for field_name in entries.keys():
            if field_name == "member_type_radios":
                pass
            else:
                print(field_name + ": " + entries[field_name].get())

    def make_forms(root, fields):
        entries = {}
        for field_name in fields.keys():
            row = Frame(root)
            lab = Label(row, width=15, text=fields[field_name])
            row.pack(side=TOP, fill=X)
            lab.pack(side=LEFT)

            if field_name == "member_type":
                form = StringVar()
                memberOpts = ["Punchcard", "Monthly", "Annual", "Student"]
                radios = []
                for text in memberOpts:
                    rb = Radiobutton(row, text=text, var=form, value=text.lower())
                    rb.pack(side=LEFT, anchor=NW)
                    radios.append(rb)
                form.set("punchcard")
                entries["member_type_radios"] = radios
            elif field_name == "dob":
                # form = DateEntry(row)   # FIXME: Datepicker not working
                # s = ttk.Style(root)
                # s.theme_use('clam')

                # form = DateEntry(row, width=12, background='darkblue', foreground='white', borderwidth=2)
                # form.pack(padx=10, pady=10)
                form = Entry(row)
                form.insert(0, "yyyy-mm-dd")
                form.pack(side=LEFT, expand=YES, fill=X)
            elif field_name == "expiration_punches":
                form = Spinbox(row, width=4,  from_=0, to=100)
                form.pack(side=LEFT, expand=NO)
            else:
                form = Entry(row)
                form.pack(side=RIGHT, expand=YES, fill=X)


            entries[field_name] = form
        return entries


    def make_filled_forms(root, fields, data):
        entries = {}
        for field_name in fields.keys():
            row = Frame(root)
            lab = Label(row, width=15, text=fields[field_name])
            row.pack(side=TOP, fill=X)
            lab.pack(side=LEFT)

            if field_name == "member_type":
                form = StringVar()
                memberOpts = ["Punchcard", "Monthly", "Annual", "Student"]
                for text in memberOpts:
                    Radiobutton(row, text=text, var=form, value=text.lower()).pack(side=LEFT, anchor=NW)
                form.set("punchcard")
            elif field_name == "dob":
                # form = DateEntry(row)   # FIXME: Datepicker not working
                # s = ttk.Style(root)
                # s.theme_use('clam')

                # form = DateEntry(row, width=12, background='darkblue', foreground='white', borderwidth=2)
                # form.pack(padx=10, pady=10)
                form = Entry(row)
                form.insert(0, "yyyy-mm-dd")
                form.pack(side=RIGHT, expand=YES, fill=X)
            else:
                form = Entry(row)
                form.pack(side=RIGHT, expand=YES, fill=X)


            entries[field_name] = form
        return entries



# create the application
splashWindow = Splash()

#
# here are method calls to the window manager class
#
splashWindow.master.title("180 Studios Login Manager")
# splashWindow.master.minsize(500, 200)
# splashWindow.master.maxsize(500, 200)
# splashWindow.master.geometry("+200+400")
splashWindow.center()

# s = ttk.Style(splashWindow.master)
# s.theme_use('clam')

my_db = LoginDatabase()

# print(my_db.log_member(3229308233395595))

# start the program
splashWindow.mainloop()
