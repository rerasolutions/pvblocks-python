import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import serial.tools.list_ports
import pickle
import os
from pvblocks import pvblocks_system


class MainWindow:
    def __init__(self, parent):
        self.settings = None
        self.root = parent
        self.online = False
        self.voltages = []
        self.currents = []
        self.pvblocks = None
        self.iv_mpp = None
        self.load_settings()

        #parent.geometry("800x600")
        parent.title("IV-Load IV-Curve")

        self.connectBtn = tk.Button(parent, text='Connect', width=25, command=self.system_connect)
        self.connectBtn.grid(column=0, row=0, columnspan=2)

        self.measureCurveBtn = tk.Button(parent, text='Measure Curve', width=25, command=self.system_measure_curve, state=tk.DISABLED)
        self.measureCurveBtn.grid(column=0, row=1, columnspan=2)

        self.fig = Figure((8, 6), dpi=100)
        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.get_tk_widget().grid(column=0, row=2, columnspan=6)
        self.draw_figure()

        point_entry = tk.Entry(parent)
        delay_entry = tk.Entry(parent)

        tk.Label(parent, text='Points').grid(row=3, column=0)
        tk.Label(parent, text='Delay [ms]').grid(row=3, column=2)
        tk.Label(parent, text='Sweep type').grid(row=3, column=4)
        point_entry.grid(row=3, column=1)
        delay_entry.grid(row=3, column=3)


        point_entry.insert(0, self.settings['points'])
        delay_entry.insert(0, self.settings['delay_ms'])

        self.cbSweepStyle = ttk.Combobox(parent, state="readonly",
                                         values=("Isc to Voc", "Voc to Isc", "Isc to Voc to Isc", "Voc to Isc to Voc"))
        self.cbSweepStyle.grid(row=3, column=5)
        self.cbSweepStyle.set(self.settings['sweepstyle'])
        self.cbSweepStyle.bind("<<ComboboxSelected>>", self.select_sweepstyle)

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
        self.online = False
        print('connect pvblocks using: ' + self.settings['serialport'])
        self.pvblocks = pvblocks_system.PvBlocks(self.settings['serialport'])
        if self.pvblocks.init_system():
            print("init ok")
            print("scanning available blocks")

            if self.pvblocks.scan_blocks():
                print("scan_blocks returns ok")
                self.iv_mpp = None
                if len(self.pvblocks.IvMppBlocks) > 0:
                    self.iv_mpp = self.pvblocks.IvMppBlocks[0]
                    self.online = True
                    print("Found IV-MPP block")
            else:
                print("scan_blocks failed")

        else:
            print("failed")

        self.update_controls()

    def disconnect(self):
        print('disconnect pvblocks')
        self.pvblocks.close_system()
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

    def select_sweepstyle(self, event):
        self.settings['sweepstyle'] = self.cbSweepStyle.get()


    def system_measure_curve(self):
        print('measure curve')
        self.voltages = []
        self.currents = []
        self.refresh_figure()
        self.save_settings()
        self.voltages = []
        self.currents = []
        curve = self.iv_mpp.measure_ivcurve(int(self.settings['points']), int(self.settings['delay_ms']), 0)

        self.voltages = curve['voltages']
        self.currents = curve['currents']
        self.refresh_figure()


    def refresh_figure(self):


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
        self.settings = {'serialport': 'COM1', 'points': '100', 'delay_ms': '20', 'sweepstyle': 'Isc to Voc'}

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
        com_ports = []
        for c in serial.tools.list_ports.comports():
            com_ports.append(c.device)


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
