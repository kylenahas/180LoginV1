import tkinter as tk
from tkinter import *
from tkinter import messagebox, StringVar, ttk
from tkcalendar import Calendar, DateEntry

import pprint

from dbManage import *
from barcodeGen import *


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

        self.scannerLabelText = tk.Label(text="-or-")
        self.scannerLabelText.pack(pady=(30, 0))
        self.scannerLabelText.pack(side='top', expand=0)

        self.addNewMemberButton = tk.Button(command=self.add_new_member_pushed)
        self.addNewMemberButton['text'] = 'Add New Member'
        self.addNewMemberButton.pack(side='left', expand=1, padx=15, pady=10)

        self.updateMemberButton = tk.Button(command=self.add_new_member_pushed)
        self.updateMemberButton['text'] = 'Update Member'
        self.updateMemberButton.pack(side='right', expand=1, padx=15, pady=10)

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

    def add_new_member_pushed(self):
        NewMemberWindow()


    def login_member(self, event):
        try:
            member_id = int(self.scannerInput.get())
            logged_member = my_db.log_member(member_id)
            info_str = "Member: " + logged_member["name_first"] + " " + logged_member["name_first"] + " logged in!\n\n"
            if my_db.retrieve_member(member_id)["member_type"] == "punchcard":
                info_str += "Punches left: " + str(logged_member["remaining_punches"])
            else:
                info_str += "Time left: " # TODO: Add time left
            messagebox.showinfo(title="Logging in:", message=info_str)
        except ValueError:
            messagebox.showwarning(title="Problem logging in member!", message="Member not found!")
        finally:
            self.scannerInput.delete(0, END)
            super().focus_force()
            self.scannerInput.focus()



class NewMemberWindow:
    entryLabels = {("First Name", "name_first"),
                   ("Last Name", "name_last"),
                   ("Email", "email"),
                   ("Phone Number", "phone")}

    def __init__(self, master=None):

        # nmw == New Member Window
        self.nmw = Toplevel()
        self.populate()
        self.center()
        self.nmw.title("Add New Member")
        style = ttk.Style(self.nmw)
        style.theme_use('clam')



    def center(self):
        self.nmw.update_idletasks()
        width = self.nmw.winfo_width()
        height = self.nmw.winfo_height()
        x = (self.nmw.winfo_screenwidth() // 2) - (width // 2)
        y = (self.nmw.winfo_screenheight() // 2) - (height // 2)
        self.nmw.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def populate(self):
        # self.scannerLabelText = tk.Label(self.nmw, text="Add New Member")
        # self.scannerLabelText.pack(pady=10)
        # self.scannerLabelText.pack(side="top", expand=0)

        self.entry_data = FormHelp.make_forms(self.nmw, {"name_first": "First Name",
                                                            "name_last": "Last Name",
                                                            "email": "Email",
                                                            "phone": "Phone Number",
                                                            "dob": "Date of Birth",
                                                            "member_type": "Member Type"})

        Button(self.nmw, text="Add Member", command=self.enter_to_db).pack(side=BOTTOM, pady=10)


    def enter_to_db(self):
        fh=FormHelp()
        printed_vals = fh.print_values(entries=self.entry_data)
        if self.validate_entries():
            print("Form ok!")
            try:
                new_member = my_db.add_member(   first_name=self.entry_data["name_first"].get(),
                                                 last_name=self.entry_data["name_last"].get(),
                                                 email=self.entry_data["email"].get(),
                                                 phone=self.entry_data["phone"].get(),
                                                 birthdate=self.entry_data["dob"].get(),
                                                 member_type_str=self.entry_data["member_type"].get())
                nm_success_str = "Successfully created member: " + new_member["name_first"] + new_member["name_last"]
                messagebox.showinfo(title="New Member Status", message=nm_success_str)

                barcode = Barcoder()

                barcode.create_barcode(new_member["id"])
                barcode.open_barcode()

                self.nmw.destroy()
            except ValueError:  # add_member() does not currently throw any exceptions.
                pass
        else:
            messagebox.showwarning(title="Problem creating member!", message="Data not completely filled")


    def validate_entries(self):
        ret = True
        for field_name in self.entry_data.keys():
            if self.entry_data[field_name].get() == "":
                ret = False
        return ret




class FormHelp:
    def print_values(self, entries):
        for field_name in entries.keys():
            print(field_name + ": " + entries[field_name].get())

    def make_forms(root, fields, dobAndType=True):
        entries = {}
        for field_name in fields.keys():
            row = Frame(root)
            lab = Label(row, width=15, text=fields[field_name])
            row.pack(side=TOP, fill=X)
            lab.pack(side=LEFT)

            if field_name == "member_type":
                form = StringVar()
                memberOpts = ["Punchcard", "Monthly", "Annual"]
                for text in memberOpts:
                    Radiobutton(row, text=text, var=form, value=text.lower()).pack(side=LEFT, anchor=NW)
                form.set("punchcard")
            elif field_name == "dob":
                # form = DateEntry(row)   # FIXME: Datepicker not working
                s = ttk.Style(root)
                s.theme_use('clam')

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
