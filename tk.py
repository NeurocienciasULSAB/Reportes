import tkinter as tk
# from tkinter import filedialog


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.entrythingy = tk.Entry()
        self.entrythingy.pack()
        # here is the application variable
        self.contents = tk.StringVar()
        # set it to some value
        self.contents.set("this is a variable")
        # tell the entry widget to watch this variable
        self.entrythingy["textvariable"] = self.contents

        # and here we get a callback when the user hits return.
        # we will have the program print out the value of the
        # application variable when the user hits return
        self.entrythingy.bind('<Key-Return>',
                              self.print_contents)

    def print_contents(self, event):
        print("hi. contents of entry is now ---->",
              self.contents.get())


if __name__ == '__main__':
    # create the application
    myapp = App()

    #
    # here are method calls to the window manager class
    #
    myapp.master.title("My Do-Nothing Application")
    myapp.master.maxsize(1000, 400)

    # start the program
    myapp.mainloop()
