from tkinter import *
from tkinter.font import Font
from datetime import datetime, date, time, timedelta
import time
import pyperclip
from enum import Enum

import config
from barcodeGen import *
from memberWindow import EditMemberWindow, EMWContext, memberSignOffs
import memberDialog as memberDialog

class SMWContext(Enum):
    Search = 1
    SplashEntry = 2
    EditMember = 3


class MemberLookup():
    def __init__(self, master=None, search_str=None, context=None):
        self.ml_enter = Toplevel()
        self.first_name_entry_sv = StringVar()
        # if not search_str:
            # nmw == New Member Window

        self.populate_searcher()
        self.center(self.ml_enter)
        self.context = SMWContext.Search
        if search_str:
            self.ml_enter.withdraw()
            self.context = context

            self.first_name_entry_sv.set(str(search_str))
            self.search_for_member(event=None)

    def populate_searcher(self):
        row1 = Frame(self.ml_enter)
        row1.pack(side=TOP, fill=X, padx=20, pady=10)
        Label(row1, text="Enter First Name").pack(side=TOP)

        row2 = Frame(self.ml_enter)
        row2.pack(side=TOP, fill=X, padx=20, pady=10)
        self.first_name_entry = Entry(row2, textvariable=self.first_name_entry_sv)
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
            self.search_string = str(self.first_name_entry_sv.get())
            self.search_results = config.appDB.query_member(name_first=self.search_string)
            self.display_search_results(self.search_results)
            self.ml_enter.destroy()
        except LookupError:
            messagebox.showwarning(title="Problem locating member!",
                                   message="No members with first name \"" + self.first_name_entry_sv.get() + "\" found!")
            self.ml_enter.deiconify()
            self.ml_enter.focus()
            self.first_name_entry.focus_force()

    def members_logged_in(self, event=None):
        # Displays members logged in during the current calendar day
        try:
            self.search_string = "Today"
            today = date.today()
            self.search_results = config.appDB.query_member(log_date=today)
            self.display_search_results(self.search_results)
            self.ml_enter.destroy()
        except LookupError:
            messagebox.showwarning(title="Problem locating members!",
                                   message="No members logged in today!")
            self.ml_enter.focus()

    def display_search_results(self, results):

        # Based heavily around: https://pyinmyeye.blogspot.com/2012/07/tkinter-multi-column-list-demo.html

        self.results_window = Toplevel()

        self.results_window.title("Search Results for: " + self.search_string)

        columns = {  "name_first": "First Name",
                     "name_last": "Last Name",
                     "id": "Member ID",
                     "join_date": "Join Date",
                     "member_type": "Member Type"}


        columnKeys=[]
        for k in columns.keys():
            columnKeys.append(k)

        self.tree = ttk.Treeview(self.results_window, columns=columnKeys, show="headings")

        for dbName in columns.keys():
            self.tree.column(dbName, width=Font().measure(columns[dbName]) + 2)
            self.tree.heading(dbName, text=columns[dbName])


        for item in results:
            arr = []
            for val in columns.keys():
                if val == "join_date":
                    join_date = datetime.strptime(item[val], '%Y-%m-%d %H:%M:%S.%f')
                    join_date_str = str(join_date.year) + "-" + str(join_date.month) + "-" + str(join_date.day)
                    arr.append(join_date_str)
                    iwidth = Font().measure(join_date_str) + 10
                elif val == "member_type":
                    member_type_str = config.member_types.get(item[val])
                    arr.append(member_type_str)
                    iwidth = Font().measure(member_type_str) + 10
                elif val == "link":
                    pass
                else:
                    arr.append(item[val])
                    iwidth = Font().measure(item[val]) + 10
                if self.tree.column(val, 'width') < iwidth:
                    self.tree.column(val, width=iwidth)
            self.tree.insert('', 'end', values=arr)


        ysb = ttk.Scrollbar(self.results_window, orient=VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(self.results_window, orient=HORIZONTAL, command=self.tree.xview)

        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set

        self.tree.grid(row=0, column=0, sticky=NSEW)
        ysb.grid(row=0, column=1, sticky=NS)
        xsb.grid(row=1, column=0, sticky=EW)

        self.results_window.rowconfigure(0, weight=1)
        self.results_window.columnconfigure(0, weight=1)

        self.buttons = Frame(self.results_window)
        self.buttons.grid()
        
        if self.context == SMWContext.Search:  # In search for members window
            Button(self.buttons, text="Print new barcode", command=self.newBarcode).grid(row=2, column=1, padx=3)
            Button(self.buttons, text="Copy Member ID",  command=self.copyMID).grid(row=2, column=2, padx=3)
            if config.sign_offs_enabled:
                Button(self.buttons, text="View Sign Offs", command=self.edit_sign_offs).grid(row=2, column=3, padx=3)
                
        elif self.context == SMWContext.SplashEntry:  # In search window popped up from splash (first) screen
            Button(self.buttons, text="Print new barcode", command=self.newBarcode).grid(row=2, column=1, padx=3)
            Button(self.buttons, text="Login Member", command=self.search_return).grid(row=2, column=2, padx=3)
            if config.sign_offs_enabled:
                Button(self.buttons, text="View Sign Offs", command=self.edit_sign_offs).grid(row=2, column=3, padx=3)

        elif self.context == SMWContext.EditMember:  # In search window popped up from edit member window
            Button(self.buttons, text="Edit Member", command=self.search_return).grid(row=2, column=1, padx=3)


        self.center(self.results_window)
        self.results_window.focus_force()


    def newBarcode(self):
        print("New Barcode")
        cur_item = self.tree.focus()

        try:
            memberID = self.tree.item(cur_item)["values"][2]
            name_first = self.tree.item(cur_item)["values"][0]
            name_last = self.tree.item(cur_item)["values"][1]
            member_type_str = self.tree.item(cur_item)["values"][4]
            member_types_inv = {v: k for k, v in config.member_types.items()}  # https://stackoverflow.com/a/483833
            member_type = member_types_inv.get(member_type_str, "").capitalize()

            print(memberID)
            barcode = Barcoder()

            name_str = name_first + " " + name_last

            if config.zebra_print_enabled:
                barcode.print_zebra(memberID, name_str=name_str, member_type_str=member_type)

            else:
                barcode.create_barcode(memberID)
                barcode.open_barcode()

            self.results_window.destroy()
        except IndexError:
            messagebox.showwarning(title="Problem locating member!",
                                   message="Please select a member from the list first")


    def copyMID(self):
        cur_item = self.tree.focus()

        try:
            memberID = self.tree.item(cur_item)["values"][2]
            # print("Member ID Copied!")
            # print(memberID)
            pyperclip.copy(memberID)
            messagebox.showinfo(title="Copy Success",
                                message="Member ID copied to clipboard. Paste in a scanner input, then press enter to use.")
            self.results_window.destroy()
        except IndexError:
            messagebox.showwarning(title="Problem locating member!",
                                   message="Please select a member from the list first")

    def printStickers(self):
        sticker = Barcoder()

        for member in self.search_results:
            member_id = member["id"]
            name_str = member["name_first"] + " " + member["name_last"]
            file = member["name_first"].lower() + "." + member["name_last"].lower()
            member_type = member["member_type"]
            member_type_str = str(config.member_types.get(member_type))
            sticker.create_sticker_image(member_id, name_str=name_str, member_type_str=member_type_str, fn=file)
        messagebox.showinfo(title="Sticker Update Success",
                            message="Stickers folder updated. See directions on how to print barcode.")
        self.results_window.destroy()

    def edit_sign_offs(self):
        cur_item = self.tree.focus()

        try:
            memberID = self.tree.item(cur_item)["values"][2]
            sign_offs = memberSignOffs(member_id=memberID)
            sign_offs.editWindow()
        except IndexError:
            messagebox.showwarning(title="Problem locating member!",
                                   message="Please select a member from the list first")

    def search_return(self):
        cur_item = self.tree.focus()
        try:
            member_id = self.tree.item(cur_item)["values"][2]
            self.results_window.destroy()

            if self.context == SMWContext.SplashEntry:

                try:
                    memberDialog.memberD(member_id=member_id)
                    pass
                except LookupError as e:
                    messagebox.showwarning(title="Problem logging in member!", message=e)
                except RuntimeError:
                    messagebox.showwarning(title="Problem logging in member!",
                                           message="Member has used all their punches!\n\nRefill punches before entry!")

            elif self.context == SMWContext.EditMember:
                EditMemberWindow(context=EMWContext.EditMember, member_id=int(member_id))

        except IndexError:
            messagebox.showwarning(title="Problem locating member!",
                                   message="Please select a member from the list first")