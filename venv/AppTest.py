import tkinter as tk

class Splash(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.grid()
        self.create_splash()

    def create_splash(self):
        self.scannerLabelText = tk.Label(text="Scan Member Card:")
        # self.scannerLabelText.grid(pady=30)
        self.scannerLabelText.grid(row=0, column=0)
        self.scannerLabelText.columnconfigure(0, weight=1)

        self.scannerInput = tk.Entry()
        # self.scannerInput.grid(pady=60)
        self.scannerInput.grid(row=1, column=0)
        self.scannerInput.focus_set()
        self.scannerInput.columnconfigure(0, weight=1)


        self.addNewMemberButton = tk.Button(command=self.add_new_member_pushed)
        self.addNewMemberButton["text"] = "Add New Member"
        self.addNewMemberButton.grid(row=2, column=0)
        self.addNewMemberButton.columnconfigure(0, weight=1)




    def clear_window(self):  # https://stackoverflow.com/a/44955479
        list = root.grid_slaves()
        for l in list:
            l.destroy()

    def add_new_member_pushed(self):
        nw = tk.Tk()
        new






# create the application
splashWindow = Splash()

#
# here are method calls to the window manager class
#
splashWindow.master.title("180 Studios Login Manager")
splashWindow.master.minsize(500, 200)
splashWindow.master.maxsize(500, 200)


# start the program
splashWindow.mainloop()