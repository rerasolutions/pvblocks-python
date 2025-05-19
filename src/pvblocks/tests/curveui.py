import datetime, pickle, os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter.filedialog import asksaveasfilename
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import serial.tools.list_ports
from pvlib.ivtools.utils import rectify_iv_curve

from pvblocks import pvblocks_system


class MainApp(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=15)
        self.pack(fill=BOTH, expand=YES)
        self.master = master

        self.status_var = ttk.StringVar(value='---')
        self.online = False
        self.is_active = False
        self.voltages = []
        self.currents = []
        self.pvblocks = None
        self.iv_mpp = None
        self.load_settings()

        self.fig = Figure((6, 4), dpi=100)
        # application variables
        self.points_var = ttk.StringVar(value=self.settings['points'])
        self.delay_var = ttk.StringVar(value=self.settings['delay_ms'])
        self.mode_var = ttk.StringVar(value='voc')
        self.sweepstyle_var = ttk.StringVar(value=self.settings['sweepstyle'])
        self.ivpoint_var = ttk.StringVar(value='---')

        self.id_var = ttk.StringVar(value='CellID')
        self.isc_var = ttk.StringVar(value='---')
        self.voc_var = ttk.StringVar(value='---')
        self.impp_var = ttk.StringVar(value='---')
        self.vmpp_var = ttk.StringVar(value='---')
        self.ff_var = ttk.StringVar(value='---')
        self.power_var = ttk.StringVar(value='---')


        self.ivparameters = {}

        self.create_menu()
        # header and labelframe option container
        option_text = "IV/MPP Load control"
        self.option_lf = ttk.Labelframe(self, text=option_text, padding=15)
        self.option_lf.pack(fill=X, expand=YES, anchor=N, pady=30)

        data_text = "Measurement"
        self.data_lf = ttk.Labelframe(self, text=data_text, padding=15)
        self.data_lf.pack(fill=X, expand=YES, anchor=N)

        status_ent = ttk.Entry(self, textvariable=self.status_var)
        status_ent.pack(side=LEFT, fill=X, expand=YES, pady=5)

        self.create_mode_row()
        self.create_curveinput_row()


        self.create_graph()
        self.create_parameters_table('ID:', self.id_var)
        self.create_parameters_table('Isc:', self.isc_var)
        self.create_parameters_table('Voc:', self.voc_var)
        self.create_parameters_table('Impp:', self.impp_var)
        self.create_parameters_table('Vmpp:', self.vmpp_var)
        self.create_parameters_table('Pmax:', self.power_var)
        self.create_parameters_table('FF:', self.ff_var)
        self.create_save_button()
        self.draw_empty_figure()
        self.update_controls()


    def print_status(self, text):
        print(text)
        self.status_var.set(text)
        self.master.update()


    def create_menu(self):
        self.menu = ttk.Menu(self.master)
        self.master.config(menu=self.menu)
        self.connect_menu = ttk.Menu(self.menu)
        self.menu.add_cascade(label='File', menu=self.connect_menu)
        self.connect_menu.add_command(label='Connect...', command=self.connect)
        self.connect_menu.add_command(label='Disconnect...', command=self.disconnect, state='disabled')
        self.connect_menu.add_separator()
        self.connect_menu.add_command(label='Exit', command=self.exit_app)
        self.configmenu = ttk.Menu(self.menu)
        self.menu.add_cascade(label='Configure', menu=self.configmenu)
        self.configmenu.add_command(label='Select serialport', command=self.open_comport_window)
        self.helpmenu = ttk.Menu(self.menu)
        self.menu.add_cascade(label='Help', menu=self.helpmenu)
        self.helpmenu.add_command(label='About', command=self.about)

    def about(self):
        Messagebox.ok('IV-Curve measurement')


    def create_parameters_table(self, caption, variable):
        isc_row = ttk.Frame(self.data_lf)
        isc_row.pack(side=TOP, expand=YES, pady=1)
        lbl = ttk.Label(master=isc_row, text=caption, width=10)
        lbl.pack(side=LEFT, padx=5)
        isc_ent = ttk.Entry(master=isc_row, textvariable=variable)
        isc_ent.pack(side=LEFT, padx=5, fill=X, expand=YES)

    def create_save_button(self):
        isc_row = ttk.Frame(self.data_lf)
        isc_row.pack(side=TOP, fill=X, pady=1)
        self.save_btn = ttk.Button(
            master=isc_row,
            text="Save data",
            command=self.save_data
        )
        self.save_btn.pack(side=TOP, fill=X, padx=5)



    def create_ivpoint_row(self):
        """Add path row to labelframe"""
        ivpoint_row = ttk.Frame(self.option_lf)
        ivpoint_row.pack(fill=X, expand=YES)
        ivpoint_lbl = ttk.Label(ivpoint_row, text="IV-Point", width=8)
        ivpoint_lbl.pack(side=LEFT, padx=(15, 0))
        ivpoint_ent = ttk.Entry(ivpoint_row, textvariable=self.ivpoint_var)
        ivpoint_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        self.measure_ivpoint_btn = ttk.Button(
            master=ivpoint_row,
            text="Measure point",
            command = self.measure_ivpoint,
            width=18
        )
        self.measure_ivpoint_btn.pack(side=LEFT, padx=5)

    def create_curveinput_row(self):
        """Add term row to labelframe"""
        term_row = ttk.Frame(self.option_lf)
        term_row.pack(fill=X, expand=YES, pady=15)
        points_lbl = ttk.Label(term_row, text="Points", width=8)
        points_lbl.pack(side=LEFT, padx=(15, 0))
        points_ent = ttk.Entry(term_row, textvariable=self.points_var)
        points_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        delay_lbl = ttk.Label(term_row, text="Delay [ms]", width=8)
        delay_lbl.pack(side=LEFT, padx=(15, 0))
        delay_ent = ttk.Entry(term_row, textvariable=self.delay_var)
        delay_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)

        sweepstyle_ent = ttk.Combobox(term_row, state="readonly", textvariable=self.sweepstyle_var,
                                      values=("Isc to Voc", "Voc to Isc", "Isc to Voc to Isc", "Voc to Isc to Voc"))
        sweepstyle_ent.pack(side=LEFT, fill=X, expand=YES)



        self.measureCurveBtn = ttk.Button(
            master=term_row,
            text="Measure Curve",
            command = self.system_measure_curve,
            width=18
        )
        self.measureCurveBtn.pack(side=LEFT, padx=5)

    def create_mode_row(self):
        """Add type row to labelframe"""
        type_row = ttk.Frame(self.option_lf)
        type_row.pack(fill=X, expand=YES, pady=15)
        type_lbl = ttk.Label(type_row, text="Mode", width=8)
        type_lbl.pack(side=LEFT, padx=(15, 0))

        voc_opt = ttk.Radiobutton(
            master=type_row,
            text="Voc mode",
            variable=self.mode_var,
            value="voc"
        )
        voc_opt.pack(side=LEFT)

        isc_opt = ttk.Radiobutton(
            master=type_row,
            text="Isc mode",
            variable=self.mode_var,
            value="isc"
        )
        isc_opt.pack(side=LEFT, padx = 5)
        voc_opt.invoke()

        self.apply_btn = ttk.Button(
            master=type_row,
            text="Apply",
            command=self.on_apply,
            width=8
        )
        self.apply_btn.pack(side=LEFT, padx=5)

        ivpoint_lbl = ttk.Label(type_row, text="IV-Point", width=8)
        ivpoint_lbl.pack(side=LEFT, padx=(15, 0))
        ivpoint_ent = ttk.Entry(type_row, textvariable=self.ivpoint_var)
        ivpoint_ent.pack(side=LEFT, fill=X, expand=YES, padx=5)
        self.measure_ivpoint_btn = ttk.Button(
            master=type_row,
            text="Measure point",
            command=self.measure_ivpoint,
            width=18
        )
        self.measure_ivpoint_btn.pack(side=LEFT, padx=5)


    def create_graph(self):
        print("Create graph")
        canvas = FigureCanvasTkAgg(self.fig, master=self.data_lf)
        canvas.get_tk_widget().pack(side=LEFT)

    def on_apply(self):
        self.print_status(self.mode_var.get())
        if self.mode_var.get() == 'isc':
            self.iv_mpp.ApplyIsc()
        else:
            self.iv_mpp.ApplyVoc()

    def system_measure_curve(self):

        self.print_status('measure curve')
        self.save_btn.configure(state=ttk.DISABLED)
        self.is_active = True
        self.update_controls()
        self.voltages = []
        self.currents = []
        self.draw_empty_figure()
        self.master.update()
        self.save_settings()

        sweepstl = 0

        if self.sweepstyle_var.get() == 'Isc to Voc':
            sweepstl = 0
        if self.sweepstyle_var.get() == 'Voc to Isc':
            sweepstl = 1
        if self.sweepstyle_var.get() == 'Isc to Voc to Isc':
            sweepstl = 8
        if self.sweepstyle_var.get() == 'Voc to Isc to Voc':
            sweepstl = 4

        curve = self.iv_mpp.measure_ivcurve(int(self.points_var.get()), int(self.delay_var.get()), sweepstl)

        self.voltages = curve['voltages']
        self.currents = curve['currents']
        self.refresh_figure()
        self.is_active = False
        self.update_controls()
        self.ivparameters = self.calculate_parameters()
        self.isc_var.set('%.3f A' % self.ivparameters['isc'])
        self.voc_var.set('%.3f V' % self.ivparameters['voc'])
        self.impp_var.set('%.3f A' % self.ivparameters['impp'])
        self.vmpp_var.set('%.3f V' % self.ivparameters['vmpp'])
        self.power_var.set('%.3f W' % self.ivparameters['pmax'])
        self.ff_var.set(f"{self.ivparameters['ff']:.2%}")
        self.save_btn.configure(state=ttk.NORMAL)


    def measure_ivpoint(self):
        self.print_status('measure point')
        self.is_active = True
        self.update_controls()
        ivpoint = self.iv_mpp.read_ivpoint()
        voltage = ivpoint.voltage
        current = ivpoint.current
        self.ivpoint_var.set('Voltage: %f V, Current: %f A, Power: %f W' % (voltage, current, voltage * current))
        self.is_active = False
        self.update_controls()



    def system_connect(self):
        if self.online:
            self.disconnect()
        else:
            self.connect()

    def exit_app(self):
        self.print_status('exit app')
        if self.online:
            self.disconnect()
        self.master.quit()

    def connect(self):
        self.online = False
        self.print_status('connect pvblocks using: ' + self.settings['serialport'])
        self.pvblocks = pvblocks_system.PvBlocks(self.settings['serialport'])
        if self.pvblocks.init_system():
            self.print_status("init ok")
            self.print_status("scanning available blocks")

            if self.pvblocks.scan_blocks():
                self.print_status("scan_blocks returns ok")
                self.iv_mpp = None
                if len(self.pvblocks.IvMppBlocks) > 0:
                    self.iv_mpp = self.pvblocks.IvMppBlocks[0]
                    self.online = True
                    self.print_status("Found IV-MPP block")
            else:
                self.print_status("scan_blocks failed")

        else:
            self.print_status("failed")

        self.update_controls()

    def disconnect(self):
        self.print_status('disconnect pvblocks')
        self.pvblocks.close_system()
        self.online = False
        self.update_controls()

    def refresh_figure(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.scatter(self.voltages, self.currents)
        ax.set_xlabel('Voltage [V]')
        ax.set_ylabel('Current [A]')
        ax.set_title('IV Curve measurement')
        self.fig.canvas.draw_idle()

    def draw_empty_figure(self):
        y = []
        x = []
        ax = self.fig.add_subplot(111)
        ax.scatter(x, y)
        ax.set_xlabel('Voltage [V]')
        ax.set_ylabel('Current [A]')
        ax.set_title('IV Curve measurement')
        self.fig.canvas.draw()

    def save_data(self):
        files = [('All Files', '*.*'),
                 ('Text Document', '*.txt')]
        filename = asksaveasfilename( initialfile=self.id_var.get() + '.txt', filetypes=files, defaultextension=files)
        if filename:
            with open(filename, "w") as f:
                f.write('IV-Curve measurement\n')
                f.write('Cell ID:\t%s\n' % self.id_var.get())
                f.write('Date:\t%s\n' % datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                f.write('Voc:\t%f V\n' % self.ivparameters['voc'])
                f.write('Isc:\t%f A\n' % self.ivparameters['isc'])
                f.write('Vmpp:\t%f V\n' % self.ivparameters['vmpp'])
                f.write('Impp:\t%f A\n' % self.ivparameters['impp'])
                f.write('Pmax:\t%f W\n' % self.ivparameters['pmax'])
                f.write(f"Fill Factor:\t{self.ivparameters['ff']:.2%}\n")
                f.write('\n')
                f.write('Voltage[V]\tCurrent[A]\n')
                for i in range(len(self.voltages)):
                    f.write(f"{self.voltages[i]}\t{self.currents[i]}\n")


    def open_comport_window(self):
        # Create a new top-level window
        comport_window = ttk.Toplevel(self.master)
        comport_window.title("Select Serial Port")
        comport_window.geometry("300x150")

        # Make the window modal
        comport_window.grab_set()

        # Label instructing the user
        label = ttk.Label(comport_window, text="Select a serial port:")
        label.pack(pady=10)

        # List of COM ports - customizable
        com_ports = []
        for c in serial.tools.list_ports.comports():
            com_ports.append(c.device)

        # Variable to hold the selected port
        selected_port = ttk.StringVar()

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
        select_button = ttk.Button(comport_window, text="Select", command=select_port)
        select_button.pack(pady=10)

    def update_controls(self):
        if self.online:
            self.connect_menu.entryconfig(0, state=ttk.DISABLED)
            self.connect_menu.entryconfig(1, state=ttk.NORMAL)
        else:
            self.connect_menu.entryconfig(0, state=ttk.NORMAL)
            self.connect_menu.entryconfig(1, state=ttk.DISABLED)
            self.save_btn.configure(state=ttk.DISABLED)


        if self.is_active:
            self.measureCurveBtn.configure(state=ttk.DISABLED)
            self.measure_ivpoint_btn.configure(state=ttk.DISABLED)
            self.apply_btn.configure(state=ttk.DISABLED)
        else:
            if self.online:
                self.measureCurveBtn.configure(state=ttk.NORMAL)
                self.measure_ivpoint_btn.configure(state=ttk.NORMAL)
                self.apply_btn.configure(state=ttk.NORMAL)
            else:
                self.measureCurveBtn.configure(state=ttk.DISABLED)
                self.measure_ivpoint_btn.configure(state=ttk.DISABLED)
                self.apply_btn.configure(state=ttk.DISABLED)

        self.master.update()

    def calculate_parameters(self):
        (v, i) = rectify_iv_curve(self.voltages, self.currents)
        p = v * i
        d = {}
        d['voc'] = v[-1]
        d['isc'] = i[0]
        index_max = np.argmax(p)
        d['impp'] = i[index_max]
        d['vmpp'] = v[index_max]
        d['pmax'] = p[index_max]
        d['ff'] = d['pmax'] / (d['voc'] * d['isc'])
        return d

    def save_settings(self):
        self.settings['points'] = self.points_var.get()
        self.settings['delay_ms'] = self.delay_var.get()
        self.settings['sweepstyle'] = self.sweepstyle_var.get()
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



if __name__ == '__main__':

    app = ttk.Window("PVBlocks IV/MPP Control", "sandstone")
    MainApp(app)
    app.mainloop()