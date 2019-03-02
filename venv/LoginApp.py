import tkinter as tk
from tkinter import *
from tkinter import messagebox, StringVar, ttk
from tkinter.font import Font
from enum import Enum

import pprint
import pyperclip

import config
from dbManage import *
from barcodeGen import *
from memberWindow import EMWContext, EditMemberWindow, memberSignOffs
from memberLookup import MemberLookup, SMWContext

import memberDialog as memberDialog





# class EMWContext(Enum):
#     NewMember = 1
#     UpdateMember = 2


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
        self.scannerInput.focus()

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
        EditMemberWindow(context=EMWContext.EditMember)

    def lookup_member_pushed(self):
        MemberLookup()


    def login_member(self, event):

        # TODO: Auto Close window after 5 seconds

        searching = False

        try:
            member_id = int(self.scannerInput.get())


            # info_str += signOffs.printSignOffs()


            # messagebox.showinfo(title="Logging in:", message=info_str)

            dialog = memberDialog.memberD(member_id=member_id)


        except ValueError as e:
            # messagebox.showwarning(title="Problem logging in member!", message=e)
            MemberLookup(search_str=self.scannerInput.get(), context=SMWContext.SplashEntry)
            searching = True
        except LookupError as e:
            messagebox.showwarning(title="Problem logging in member!", message=e)
        except RuntimeError:
            messagebox.showwarning(title="Problem logging in member!", message="Member has used all their punches!\n\nRefill punches before entry!")
        finally:
            # dialog.destroy()
            self.scannerInput.delete(0, END)
            if not searching:
                super().focus_force()
                self.scannerInput.focus()




# create the application
splashWindow = Splash()

#
# here are method calls to the window manager class
#
splashWindow.master.title("180 Studios Login Manager")

splashWindow.center()

# start the program
splashWindow.mainloop()
