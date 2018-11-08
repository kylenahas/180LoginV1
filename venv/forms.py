from tkinter import *

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
                form.grid(row=row_number, column=1, columnspan=cs, sticky=W)

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
