import tkinter as tk
from tkinter import *
from tkinter import messagebox, StringVar, ttk
from tkinter.font import Font
from enum import Enum

import pprint
import pyperclip


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

        tk.Button(command=self.add_new_member_pushed, text="Add New Member").pack(side='left', expand=1, padx=5, pady=10)

        tk.Button(command=self.update_member_pushed, text="Update Member").pack(side='right', expand=1, padx=5, pady=10)

        tk.Button(command=self.lookup_member_pushed, text="Lookup Member").pack(side='bottom', expand=1, padx=5, pady=10)

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
        EditMemberWindow(context=EMWContext.NewMember)

    def update_member_pushed(self):
        EditMemberWindow(context=EMWContext.UpdateMember)

    def lookup_member_pushed(self):
        MemberLookup()


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
                elif form == "dob_arr":
                    for spinbox in self.entry_data[form]:
                        spinbox.config(state=NORMAL)
                else:
                    self.entry_data[form].config(state=NORMAL)
                    self.entry_data[form].delete(0, END)
                    self.entry_data[form].insert(0, member_info[form])

            self.sync_dob()

            self.add_punches_button.config(state=NORMAL)


        except ValueError:
            messagebox.showwarning(title="Problem retrieving member data!", message="Member not found!")
            self.nmw.focus_force()
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
            except Exception as e:
                messagebox.showwarning(title="Problem adding member!", message="An exception occured:\n" + str(e))
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


class FormHelp:
    def print_values(self, entries):
        for field_name in entries.keys():
            if field_name == "member_type_radios" or field_name == "dob_arr":
                pass
            elif field_name == "member_opts" or field_name == "member_opts_vars":
                pass
            else:
                print(field_name + ": " + entries[field_name].get())

    def make_forms(root, fields):
        entries = {}
        row = Frame(root)
        row.grid()
        row_number = 0
        cs = 6  #Column Span
        for field_name in fields.keys():
            # row = Frame(root)
            lab = Label(row, width=15, text=fields[field_name])
            # row.pack(side=TOP, fill=X)
            # lab.pack(side=LEFT)
            # row.grid()
            lab.grid(row=row_number, column=0, sticky=NSEW)
            root.rowconfigure(row_number, weight=1)
            root.columnconfigure(0, weight=1)

            if field_name == "member_type":
                form = StringVar()
                memberOpts = ["Punchcard", "Monthly", "Student",
                              "Organization", "Annual", "Volunteer"]
                radios = []
                i=0
                for text in memberOpts:
                    rb = Radiobutton(row, text=text, var=form, value=text.lower())
                    if i % 6 == 0 and i != 0:
                        row_number += 1
                    rb.grid(row=row_number, column=(i % 6)+1, columnspan=2, sticky=W)
                    radios.append(rb)
                    i += 2
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
                # form.pack(side=LEFT, expand=YES, fill=X)



                month = Spinbox(row, width=2, from_=1, to=12)
                day = Spinbox(row, width=2, from_=1, to=31)
                year = Spinbox(row, width=4, from_=1900, to=2018)


                dob = [year, month, day]
                entries["dob_arr"] = dob

                Label(row, text="Month:").grid(row=row_number, column=1)
                month.grid(row=row_number, column=2)
                Label(row, text="Day:").grid(row=row_number, column=3)
                day.grid(row=row_number, column=4)
                Label(row, text="Year:").grid(row=row_number, column=5)
                year.grid(row=row_number, column=6)



            elif field_name == "expiration_punches":
                form = Spinbox(row, width=4,  from_=0, to=100)
                form.grid(row=row_number, column=1, columnspan=cs)

            elif field_name == "member_opts":

                form = [StringVar(), StringVar(), StringVar()]
                form[1].set("0")
                form[2].set("0")
                addon = Checkbutton(row, text="Add-On", variable=form[1])
                org = Checkbutton(row, text="Organization", variable=form[2])

                addon.grid(row=row_number, column=1, columnspan=2, sticky=W)
                org.grid(row=row_number, column=3, columnspan=2, sticky=W)

                row_number+=1
                link_id = Entry(row, state=DISABLED, textvariable=form[0])
                link_id.grid(row=row_number, column=1, columnspan=4, sticky=W)

                entries["member_opts_vars"] = [link_id, addon, org]
            else:
                form = Entry(row)
                form.grid(row=row_number, column=1, columnspan=cs, sticky=NSEW)

            row_number+=1


            entries[field_name] = form
        return entries




class MemberLookup():
    def __init__(self, master=None):

        # nmw == New Member Window
        self.ml_enter = Toplevel()
        self.populate_searcher()
        self.center(self.ml_enter)


    def populate_searcher(self):
        row1 = Frame(self.ml_enter)
        row1.pack(side=TOP, fill=X, padx=20, pady=10)
        Label(row1, text="Enter First Name").pack(side=TOP)

        row2 = Frame(self.ml_enter)
        row2.pack(side=TOP, fill=X, padx=20, pady=10)
        self.first_name_entry = Entry(row2)
        self.first_name_entry.pack()
        self.first_name_entry.focus()
        self.first_name_entry.bind('<Return>', self.search_for_member)

        row3 = Frame(self.ml_enter)
        row3.pack(side=TOP, fill=X, padx=20, pady=10)
        Button(row3, command=self.search_for_member, text="Search for Member").pack()
        Button(row3, command=self.members_logged_in, text="Members here now").pack()



    def center(self, root):
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def search_for_member(self, event=None):
        try:
            self.search_string = str(self.first_name_entry.get())
            self.search_results = my_db.query_member(name_first=self.search_string)
            self.display_search_results(self.search_results)
            self.ml_enter.destroy()
        except ValueError:
            messagebox.showwarning(title="Problem locating member!",
                                   message="No members with first name \"" + self.first_name_entry.get() + "\" found!")
            self.ml_enter.focus()
            self.first_name_entry.focus_force()

    def members_logged_in(self, event=None):
        try:
            self.search_string = "Today"
            self.search_results = my_db.query_member(log_date=True)
            self.display_search_results(self.search_results)
            self.ml_enter.destroy()
        except ValueError:
            messagebox.showwarning(title="Problem locating members!",
                                   message="No members logged in today!")
            self.ml_enter.focus()

    def display_search_results(self, results):

        # Based heavily around: https://pyinmyeye.blogspot.com/2012/07/tkinter-multi-column-list-demo.html

        self.rwin = Toplevel()

        self.rwin.title("Search Results for: " + self.search_string)

        columns = {  "name_first": "First Name",
                     "name_last": "Last Name",
                     "id": "Member ID",
                     "dob": "Date of Birth",
                     "member_type": "Member Type"}


        columnKeys=[]
        for k in columns.keys():
            columnKeys.append(k)

        self.tree = ttk.Treeview(self.rwin, columns=columnKeys, show="headings")

        for dbName in columns.keys():
            # tree.heading(c, text=c.title(),
            #                   command=lambda c=c: self._column_sort(c, MCListDemo.SortDir))
            self.tree.column(dbName, width=Font().measure(columns[dbName]) + 2)
            self.tree.heading(dbName, text=columns[dbName])


        for item in results:
            arr = []
            for val in columns.keys():
                arr.append(item[val])
                iwidth = Font().measure(item[val]) + 10
                if self.tree.column(val, 'width') < iwidth:
                    self.tree.column(val, width=iwidth)
            self.tree.insert('', 'end', values=arr)


        ysb = ttk.Scrollbar(self.rwin, orient=VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(self.rwin, orient=HORIZONTAL, command=self.tree.xview)

        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set

        self.tree.grid(row=0, column=0, sticky=NSEW)
        ysb.grid(row=0, column=1, sticky=NS)
        xsb.grid(row=1, column=0, sticky=EW)

        self.rwin.rowconfigure(0, weight=1)
        self.rwin.columnconfigure(0, weight=1)

        self.buttons = Frame(self.rwin)
        self.buttons.grid()

        Button(self.buttons, text="Print new barcode", command=self.newBarcode).grid(row=2, column=1)
        Button(self.buttons, text="Copy Member ID",  command=self.copyMID).grid(row=2, column=2)
        Button(self.buttons, text="Print list to stickers",  command=self.printStickers).grid(row=2, column=3)

        self.center(self.rwin)
        self.rwin.focus_force()


    def newBarcode(self):
        print("New Barcode")
        cur_item = self.tree.focus()

        try:
            memberID = self.tree.item(cur_item)["values"][2]
            print(memberID)
            barcode = Barcoder()

            barcode.create_barcode(memberID)
            barcode.open_barcode()
            self.rwin.destroy()
        except IndexError:
            messagebox.showwarning(title="Problem locating member!",
                                   message="Please select a member from the list first")


    def copyMID(self):
        cur_item = self.tree.focus()

        try:
            memberID = self.tree.item(cur_item)["values"][2]
            print("Member ID Copied!")
            print(memberID)
            pyperclip.copy(memberID)
            messagebox.showinfo(title="Copy Success",
                                message="Member ID copied to clipboard. Paste in a scanner input, then press enter to use.")
            self.rwin.destroy()
        except IndexError:
            messagebox.showwarning(title="Problem locating member!",
                                   message="Please select a member from the list first")

    def printStickers(self):
        sticker = Barcoder()
        for member in self.search_results:
            member_id = member["id"]
            name_str = member["name_first"] + " " + member["name_last"]
            file = member["name_first"].lower() + "." + member["name_last"].lower()
            member_type = member["member_type"].capitalize()
            sticker.create_sticker_image(member_id, name_str=name_str, member_type_str=member_type, fn=file)



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
