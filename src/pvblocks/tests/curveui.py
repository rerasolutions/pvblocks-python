import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import pickle
import os


class MainWindow:
    def __init__(self, parent):
        self.settings = None
        self.root = parent
        self.online = False
        self.load_settings()





        parent.geometry("300x200")
        parent.title("IV-Load IV-Curve")
        self.label = tk.Label(parent, text='The Main Window')
        self.label.pack()

        self.button = tk.Button(parent, text='Connect', width=25, command=self.system_connect)
        self.button.pack()

        self.menu = tk.Menu(parent)
        parent.config(menu=self.menu)
        self.connect_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label='File', menu=self.connect_menu)
        self.connect_menu.add_command(label='Connect...', command=self.connect)
        self.connect_menu.add_command(label='Close...', command=self.disconnect, state='disabled')
        self.connect_menu.add_separator()
        self.connect_menu.add_command(label='Exit', command=parent.quit)
        self.configmenu = tk.Menu(self.menu)
        self.menu.add_cascade(label='Configure', menu=self.configmenu)
        self.configmenu.add_command(label='Select serialport', command=self.open_comport_window)
        self.helpmenu = tk.Menu(self.menu)
        self.menu.add_cascade(label='Help', menu=self.helpmenu)
        self.helpmenu.add_command(label='About')




    def connect(self):
        print('connect pvblocks using: ' + self.settings['serialport'])

        self.connect_menu.entryconfig(0, state=tk.DISABLED)
        self.connect_menu.entryconfig(1, state=tk.NORMAL)
        self.button.configure(text="Disconnect")
        self.online = True

    def disconnect(self):
        print('disconnect pvblocks')
        self.connect_menu.entryconfig(0, state=tk.NORMAL)
        self.connect_menu.entryconfig(1, state=tk.DISABLED)
        self.button.configure(text="Connect")
        self.online = False

    def system_connect(self):
        if self.online:
            self.disconnect()
        else:
            self.connect()

    def save_settings(self):
        with open('settings.pkl', 'wb') as f:
            pickle.dump(self.settings, f)

    def load_settings(self):
        self.settings = {'serialport': 'COM1'}

        if os.path.isfile('settings.pkl'):
            with open('settings.pkl', 'rb') as f:
                self.settings = pickle.load(f)
        else:
            with open('settings.pkl', 'wb') as f:
                pickle.dump(self.settings, f)

        for key in self.settings.keys():
            print(self.settings[key])


    def open_comport_window(self):
        # Create a new top-level window
        comport_window = tk.Toplevel(self.root)
        comport_window.title("Select Serial Port")
        comport_window.geometry("300x150")

        # Make the window modal
        comport_window.grab_set()

        # Label instructing the user
        label = tk.Label(comport_window, text="Select a serial port:")
        label.pack(pady=10)

        # List of COM ports - customizable
        com_ports = serial.tools.list_ports.comports()

        # Variable to hold the selected port
        selected_port = tk.StringVar()

        # Combobox for selecting COM port
        combo = ttk.Combobox(comport_window, values=com_ports, textvariable=selected_port)
        combo.pack(pady=5)
        combo.current(0)  # Set default selection

        # Function to handle selection
        def select_port():
            self.settings['serialport'] = selected_port.get()
            self.save_settings()
            comport_window.grab_release()
            comport_window.destroy()

        # Button to confirm selection
        select_button = tk.Button(comport_window, text="Select", command=select_port)
        select_button.pack(pady=10)


root = tk.Tk()
MainWindow(root)
root.mainloop()
