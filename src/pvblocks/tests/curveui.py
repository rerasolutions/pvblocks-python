import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import serial.tools.list_ports
import pickle
import os


class MainWindow:
    def __init__(self, parent):
        self.settings = None
        self.root = parent
        self.online = False
        self.voltages = []
        self.currents = []
        self.load_settings()
        self.adder = 0.1;

        parent.geometry("800x600")
        parent.title("IV-Load IV-Curve")


        self.connectBtn = tk.Button(parent, text='Connect', width=25, command=self.system_connect)
        self.connectBtn.pack()

        self.measureCurveBtn = tk.Button(parent, text='Measure Curve', width=25, command=self.system_measure_curve, state=tk.DISABLED)
        self.measureCurveBtn.pack()

        self.fig = Figure((6, 6), dpi=80)
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.get_tk_widget().pack()
        self.draw_figure()

        self.menu = tk.Menu(parent)
        parent.config(menu=self.menu)
        self.connect_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label='File', menu=self.connect_menu)
        self.connect_menu.add_command(label='Connect...', command=self.connect)
        self.connect_menu.add_command(label='Disconnect...', command=self.disconnect, state='disabled')
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
        self.online = True
        self.update_controls()

    def disconnect(self):
        print('disconnect pvblocks')
        self.online = False
        self.update_controls()

    def update_controls(self):
        if self.online:
            self.connect_menu.entryconfig(0, state=tk.DISABLED)
            self.connect_menu.entryconfig(1, state=tk.NORMAL)
            self.measureCurveBtn.configure(state='normal')
            self.connectBtn.configure(text="Disconnect")
        else:
            self.connect_menu.entryconfig(0, state=tk.NORMAL)
            self.connect_menu.entryconfig(1, state=tk.DISABLED)
            self.connectBtn.configure(text="Connect")
            self.measureCurveBtn.configure(state='disabled')

    def system_connect(self):
        if self.online:
            self.disconnect()
        else:
            self.connect()


    def system_measure_curve(self):
        print('measure curve')
        self.voltages = []
        self.currents = []

        self.voltages = [0,1,2,3,4,5,6,7,8,9]
        self.currents = [3,5,2,1,3,4,6,5,4,5]
        self.refresh_figure()


    def refresh_figure(self):
        y = [(i+self.adder) ** 2 for i in range(101)]
        self.adder = self.adder + 2
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.scatter(self.voltages, self.currents)
        self.fig.canvas.draw_idle()

    def draw_figure(self):
        y = []
        x = []
        ax = self.fig.add_subplot(111)
        ax.scatter(x, y)
        self.fig.canvas.draw()

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
