import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, filedialog, StringVar, ttk
import os
import sys
import time
from plotly.offline import plot

import config
import dbManage
from barcodeGen import Barcoder
from chartsHelper import chartsHelper

class StdoutRedirector(object): # https://stackoverflow.com/q/18517084
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self,string):
        self.text_space.insert('end', string)
        self.text_space.see('end')


class Admin(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        # self.print_all_members_barcode()
        self.buttons = {self.get_all_users: "Print members to list",
                        self.print_all_members_barcode: "Print All Barcodes",
                        self.delete_member: "Delete Member",
                        self.weekly_plot: "Weekly Attendance",
                        self.clear: "Clear Console"}
        self.create_splash()
        self.center()

        sys.stdout = StdoutRedirector(self.console)
        sys.stderr = StdoutRedirector(self.console)



    def create_splash(self):
        for func in self.buttons.keys():
            tk.Button(command=func, text=self.buttons.get(func)).pack()
        self.console = Text(width=60, height=40)
        self.console.pack()

    def center(self):
        # https://stackoverflow.com/a/10018670
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.master.minsize(width=width, height=height)
        self.master.maxsize(width=width, height=height)

    def print(self, write):
        self.console.insert(END, str(write) + "\n")

    def clear(self):
        self.console.delete(0.0, END)

    def get_all_users(self):
        print(len(config.appDB.membersDB.all()))
        # self.clear()
        for member in config.appDB.membersDB:
            name = member.get("name_first") + " " + member.get("name_last")
            member_id = str(member.get("id"))
            type = member.get("member_type")
            self.print(name + " :: " + type + " :: " + member_id)

    def print_all_members_barcode(self):
        bc = Barcoder()
        num_members = str(len(config.appDB.membersDB.all()))

        delay = 0.1

        if messagebox.askyesno("Print?", "Print " + num_members + " barcodes?"):
            for member in config.appDB.membersDB:
                if not member.get("deleted"):
                    name = member.get("name_first") + " " + member.get("name_last")
                    member_id = str(member.get("id"))
                    type = member.get("member_type").capitalize()
                    if type == "student_annual":
                        type = "student"
                    print(name + " :: " + type + " :: " + member_id)
                    bc.print_zebra(member_id, name, type, dry_run=True)
                    self.master.update()
                    time.sleep(delay)


    def delete_member(self):
        member_id = simpledialog.askinteger("Input", "Member to delete?")
        if member_id:
            config.appDB.delete_member(member_id)
        print("Deleted: " + str(member_id))

    def weekly_plot(self):
        if platform.system() == "Windows":
            initialdir = "C:/"
        else:
            initialdir = "/"
        logfile = filedialog.askopenfilename(initialdir=initialdir, title="Select file",
                                              filetypes=(("json files", "*.json"), ("all files", "*.*")))
        print(logfile)
        ch = chartsHelper()
        ch.calculate_attendence()
        plot(ch.create_attendence_chart())




if __name__ == "__main__":
    ad = Admin()
    ad.mainloop()