from tkinter import *

def connect():
    print('connect pvblocks')
    connect_menu.entryconfig(0, state=DISABLED)
    connect_menu.entryconfig(1, state=NORMAL)

def disconnect():
    print('disconnect pvblocks')
    connect_menu.entryconfig(0, state=NORMAL)
    connect_menu.entryconfig(1, state=DISABLED)


root = Tk()
menu = Menu(root)
root.config(menu=menu)
connect_menu = Menu(menu)
menu.add_cascade(label='File', menu=connect_menu)
connect_menu.add_command(label='Connect...', command=connect)
connect_menu.add_command(label='Close...', command=disconnect, state='disabled')
connect_menu.add_separator()
connect_menu.add_command(label='Exit', command=root.quit)
helpmenu = Menu(menu)
menu.add_cascade(label='Help', menu=helpmenu)
helpmenu.add_command(label='About')
mainloop()