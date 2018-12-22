import tkinter as tk
from tkinter import *
from tkinter import messagebox, StringVar, ttk
from tkinter.font import Font
from enum import Enum
import datetime
from dateutil import relativedelta

import config
from dbManage import *
from memberWindow import memberSignOffs

class memberD():
    def __init__(self, member_id):
        self.info_win = Toplevel()
        # self.info_win.iconify()
        title = "Logging in:"
        message = self.string_generate(member_id=member_id)

        self.info_win.title(title)

        Label(self.info_win, text=message, anchor="w", justify=LEFT).pack(padx=20, pady=20)
        ok = Button(self.info_win, text="OK", anchor="w", padx=15, command=self.destroy, state=ACTIVE)
        # ok.config(relief=SUNKEN)
        ok.pack(side='right', padx=15, pady=15)
        self.center(self.info_win)
        self.info_win.focus_force()
        self.info_win.bind_all("<Return>", lambda x: self.destroy())
        # ok.focus()
        # self.info_win.configure(background="#abcdef")
        # self.info_win.deiconify()
        self.info_win.after(3000, self.destroy)
        self.info_win.wait_window()



    def center(self, root):
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        root.focus()


    def destroy(self):
        self.info_win.destroy()

    def string_generate(self, member_id):
        try:
            logged_member = config.appDB.log_member(member_id)
            if config.sign_offs_enabled:
                signOffs = memberSignOffs(member_id)
            info_str = "Member: " + logged_member["name_first"] + " " + logged_member["name_last"] + " logged in!\n\n"
            member_type = config.appDB.retrieve_member(member_id)["member_type"]
            if member_type == "punchcard":
                info_str += "Punches left: " + str(logged_member["remaining_punches"])

            # 5036847361558019
            elif member_type == "monthly" or member_type == "annual" or member_type == "student" or member_type == "student_annual":
                exp_date_str = str(config.appDB.retrieve_member(member_id)["expiration_date"])
                exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d %H:%M:%S.%f')

                if datetime.now() < exp_date:
                    remaining = relativedelta.relativedelta(exp_date, datetime.now())
                    info_str += "Membership expires in:\n"

                    if remaining.years == 1:
                        info_str += str(remaining.years) + " year, "
                    if remaining.years > 1:
                        info_str += str(remaining.years) + " years, "

                    if remaining.months == 1:
                        info_str += str(remaining.months) + " month, and "
                    if remaining.months > 1:
                        info_str += str(remaining.months) + " months, and "

                    if remaining.days == 1:
                        info_str += str(remaining.days) + " day."
                    if remaining.days > 1:
                        info_str += str(remaining.days) + " days."

                else:
                    info_str += "Membership is EXPIRED!!!"


            return info_str
        except Exception as e:
            self.destroy()
            raise e