import sys
import time
import numpy as np
import pyqtgraph as pg

from PyQt5 import uic
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

# Switch to using white background and black foreground
# pg.setConfigOption('background', 'w')
# pg.setConfigOption('foreground', 'k')


def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


sys.excepthook = trap_exc_during_debug


class playbackThread(QThread):

    sig_step = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)

    # def __del__(self):
    #     self.wait()

    def run(self):
        while(True):
            self.sig_step.emit()
            time.sleep(0.1)


class PowerPlotApp(QMainWindow):

    # calculation functions
    def U(self,
            U0=None,
            Uangle=None,
            phi=None,
            ):
        if U0 is None:
            U0 = self.U0
        if Uangle is None:
            Uangle = self.Uangle_rad
        if phi is None:
            phi = self.inst_phi_rad
        return U0 * np.exp(1j*Uangle) * np.exp(1j*phi)

    def I(self,
            I0=None,
            Iangle=None,
            phi=None,
            ):
        if I0 is None:
            I0 = self.I0
        if Iangle is None:
            Iangle = self.Iangle_rad
        if phi is None:
            phi = self.inst_phi_rad
        return I0 * np.exp(1j*Iangle) * np.exp(1j*phi)

    def S1(self,
            U0=None,
            Uangle=None,
            I0=None,
            Iangle=None,
            phi=None,
            ):
        if U0 is None:
            U0 = self.U0
        if Uangle is None:
            Uangle = self.Uangle_rad
        if I0 is None:
            I0 = self.I0
        if Iangle is None:
            Iangle = self.Iangle_rad
        if phi is None:
            phi = self.inst_phi_rad
        return self.U(U0=U0, Uangle=Uangle, phi=phi) * \
            self.I(I0=I0, Iangle=Iangle, phi=phi)

    def S0(self,
            U0=None,
            Uangle=None,
            I0=None,
            Iangle=None,
            phi=None,
            ):
        if U0 is None:
            U0 = self.U0
        if Uangle is None:
            Uangle = self.Uangle_rad
        if I0 is None:
            I0 = self.I0
        if Iangle is None:
            Iangle = self.Iangle_rad
        if phi is None:
            phi = self.inst_phi_rad
        return self.U(U0=U0, Uangle=Uangle, phi=phi) * \
            np.conj(self.I(I0=I0, Iangle=Iangle, phi=phi))

    def S(self,
            U0=None,
            Uangle=None,
            I0=None,
            Iangle=None,
            phi=None,
            ):
        if U0 is None:
            U0 = self.U0
        if Uangle is None:
            Uangle = self.Uangle_rad
        if I0 is None:
            I0 = self.I0
        if Iangle is None:
            Iangle = self.Iangle_rad
        if phi is None:
            phi = self.inst_phi_rad
        return self.S0(U0=U0, Uangle=Uangle, I0=I0, Iangle=Iangle, phi=phi) + \
            self.S1(U0=U0, Uangle=Uangle, I0=I0, Iangle=Iangle, phi=phi)

    def __init__(self):
        super(PowerPlotApp, self).__init__()
        uic.loadUi('powerplots.ui', self)
        self.show()

        # initialize calculation values
        self.U0 = 0
        self.Uangle_deg = 0
        self.Uangle_rad = 0
        self.I0 = 0
        self.Iangle_deg = 0
        self.Iangle_rad = 0
        self.inst_phi_deg = 0
        self.inst_phi_rad = 0

        self.deg_range = 0
        self.phi_range = 0

        self.Ucomplex = 0 + 0j
        self.Icomplex = 0 + 0j
        self.S0complex = 0 + 0j
        self.S1complex = 0 + 0j
        self.Scomplex = 0 + 0j

        self.init_phasor_plot()
        self.init_sinewave_plot()

        # get initial values from GUI
        self.voltage_amplitude_changed()
        self.voltage_phase_angle_changed()
        self.current_amplitude_changed()
        self.current_phase_angle_changed()

        # signal connectors for voltage_amplitude
        self.voltage_amplitude.valueChanged.connect(
            self.voltage_amplitude_changed
            )

        # signal connectors for voltage_phase_angle
        self.voltage_phase_angle.valueChanged.connect(
            self.voltage_phase_angle_changed
            )

        # signal connectors for current_amplitude
        self.current_amplitude.valueChanged.connect(
            self.current_amplitude_changed
            )

        # signal connectors for current_phase_angle
        self.current_phase_angle.valueChanged.connect(
            self.current_phase_angle_changed
            )

        # # signal connectors for apparent_power
        self.apparent_power.valueChanged.connect(
            self.apparent_power_changed
            )

        # # signal connectors for active_power
        self.active_power.valueChanged.connect(
            self.active_power_changed
            )

        # # signal connectors for reactive_power
        self.reactive_power.valueChanged.connect(
            self.reactive_power_changed
            )

        # signal connectors for playback
        self.instantaneous_phase_angle.valueChanged.connect(
            self.instantaneous_phase_angle_changed
            )

        self.playback_button.clicked.connect(self.start_playback)
        self.playback_reset_button.clicked.connect(
            self.set_instantaneous_phase
            )

    def voltage_amplitude_changed(self):
        self.U0 = self.voltage_amplitude.value() / 100
        self.update_calculations()
        self.voltage_amplitude_display.display("{:0.2f}".format(self.U0))
        self.update_power_dials_displays()
        self.update_plots()

    def voltage_phase_angle_changed(self):
        self.Uangle_deg = (self.voltage_phase_angle.value() + 90) % 360 - 180
        self.Uangle_rad = self.Uangle_deg / 180 * np.pi
        self.update_calculations()
        self.voltage_phase_display.display(int(self.Uangle_deg))
        self.update_power_dials_displays()
        self.update_plots()

    def current_amplitude_changed(self):
        self.I0 = self.current_amplitude.value() / 100
        self.update_calculations()
        self.current_amplitude_display.display("{:0.2f}".format(self.I0))
        self.update_power_dials_displays()
        self.update_plots()

    def current_phase_angle_changed(self):
        self.Iangle_deg = (self.current_phase_angle.value() + 90) % 360 - 180
        self.Iangle_rad = self.Iangle_deg / 180 * np.pi
        self.update_calculations()
        self.current_phase_display.display(int(self.Iangle_deg))
        self.update_power_dials_displays()
        self.update_plots()

    def apparent_power_changed(self):
        self.update_current_from_power(changed='S')
        self.update_calculations()
        self.update_power_dials_displays(exclude='S')
        self.update_plots()

    def active_power_changed(self):
        self.update_current_from_power(changed='P')
        self.update_calculations()
        self.update_power_dials_displays(exclude='P')
        self.update_plots()

    def reactive_power_changed(self):
        self.update_current_from_power(changed='Q')
        self.update_calculations()
        self.update_power_dials_displays(exclude='Q')
        self.update_plots()

    def instantaneous_phase_angle_changed(self):
        self.inst_phi_deg = \
            (self.instantaneous_phase_angle.value() + 90) % 360 - 180
        self.inst_phi_rad = self.inst_phi_deg / 180 * np.pi
        self.update_calculations()
        self.instantaneous_phase_display.display(self.inst_phi_deg)
        self.update_plots()

    def update_current_from_power(self, changed):
        if changed is 'S':
            S = self.apparent_power.value() / 100
            self.I0 = S / self.U0
        if changed is 'P':
            P = self.active_power.value() / 100
            S = np.abs(P + 1j*np.imag(self.S0complex))
            self.I0 = S / self.U0
            self.Iangle_rad = -np.arccos(P/S) + self.Uangle_rad
            self.Iangle_deg = self.Iangle_rad / np.pi * 180
        if changed is 'Q':
            Q = self.reactive_power.value() / 100
            S = np.abs(np.real(self.S0complex) + 1j*Q)
            self.I0 = S / self.U0
            self.Iangle_rad = -np.arcsin(Q/S) + self.Uangle_rad
            self.Iangle_deg = self.Iangle_rad / np.pi * 180

        self.current_amplitude.blockSignals(True)
        self.current_amplitude.setValue(self.I0 * 100)
        self.current_amplitude.blockSignals(False)
        self.current_amplitude_display.display("{:0.2f}".format(self.I0))

        self.current_phase_angle.blockSignals(True)
        self.current_phase_angle.setValue((self.Iangle_deg + 90 + 360) % 360)
        self.current_phase_angle.blockSignals(False)
        self.current_phase_display.display(int(self.Iangle_deg))

    def update_power_dials_displays(self, exclude=''):
        S = np.abs(self.S0complex)
        self.apparent_power_display.display(
            "{:0.2f}".format(S)
            )
        if 'S' not in exclude:
            self.apparent_power.blockSignals(True)
            self.apparent_power.setValue(S*100)
            self.apparent_power.blockSignals(False)

        P = np.real(self.S0complex)
        self.active_power_display.display(
            "{:0.2f}".format(P)
            )
        if 'P' not in exclude:
            self.active_power.blockSignals(True)
            self.active_power.setValue(P*100)
            self.active_power.blockSignals(False)

        Q = np.imag(self.S0complex)
        self.reactive_power_display.display(
            "{:0.2f}".format(Q)
            )
        if 'Q' not in exclude:
            self.reactive_power.blockSignals(True)
            self.reactive_power.setValue(Q*100)
            self.reactive_power.blockSignals(False)

    def start_playback(self):
        self.playback_reset_button.setEnabled(False)
        self.instantaneous_phase_angle.setEnabled(False)
        self.playback_button.setText('Pause')
        self.playback_button.clicked.disconnect(self.start_playback)
        self.playback_button.clicked.connect(self.stop_playback)

        self.playback_thread = playbackThread()
        self.playback_thread.sig_step.connect(
            self.increment_instantaneous_phase
            )
        self.playback_thread.start()
        self.playback_button.clicked.connect(self.playback_thread.terminate)

    def stop_playback(self):
        self.playback_reset_button.setEnabled(True)
        self.instantaneous_phase_angle.setEnabled(True)
        self.playback_button.setText('Play')
        self.playback_button.clicked.disconnect(self.stop_playback)
        self.playback_button.clicked.connect(self.start_playback)

    def init_phasor_plot(self):
        xmin = -2
        xmax = 2
        ymin = -2
        ymax = 2

        self.phasor_plot.setTitle('Phasors')
        self.phasor_plot.setLabel('bottom', text='Real', units='p.u.')
        self.phasor_plot.setLabel('left', text='Imaginary', units='p.u.')
        self.phasor_plot.showGrid(x=True, y=True)
        self.phasor_plot.getAxis('bottom').setTickSpacing(major=1, minor=.1)
        self.phasor_plot.getAxis('left').setTickSpacing(major=1, minor=.1)
        self.phasor_plot.addLegend(offset=[30, -30])
        self.phasor_plot.setAspectLocked(True, ratio=1)
        self.phasor_plot.disableAutoRange()
        self.phasor_plot.setYRange(min=ymin, max=ymax)
        self.phasor_plot.setXRange(min=xmin, max=xmax)

        self.phasor_plot.addLine(
            x=0,
            pen=pg.mkPen('w', width=2, style=Qt.DashLine),
            z=-1,
            )
        self.phasor_plot.addLine(
            y=0,
            pen=pg.mkPen('w', width=2, style=Qt.DashLine),
            z=-1,
            )

        # self.phasor_plot.canvas.axes.axhline(color='black', zorder=1, lw=1)
        # self.phasor_plot.canvas.axes.axvline(color='black', zorder=1, lw=1)
        # unity_circle = np.exp(-1j*np.arange(0, 2*np.pi, np.pi/180))
        # self.phasor_plot.canvas.axes.plot(
        #     np.real(unity_circle),
        #     np.imag(unity_circle), '0.2', zorder=-1, lw=1)

        self.phasor_lines = {}
        self.phasor_lines['U'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='b', width=3),
            name='U',
            )
        self.phasor_lines['I'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='r', width=3),
            name='I',
            )
        self.phasor_lines['S'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='g', width=3),
            name='S',
            )

        self.phasor_circles = {}
        self.phasor_circles['U'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='b', width=1, style=Qt.DotLine),
            )
        self.phasor_circles['I'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='r', width=1, style=Qt.DotLine),
            )
        self.phasor_circles['S'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='g', width=1, style=Qt.DotLine),
            )

        # phasor valuelines
        self.phasor_values = {}
        self.phasor_values['U'] = self.phasor_plot.addLine(
            x=0,
            pen=pg.mkPen(color='b', width=2, style=Qt.DotLine))
        self.phasor_values['I'] = self.phasor_plot.addLine(
            x=0,
            pen=pg.mkPen(color='r', width=2, style=Qt.DotLine))
        self.phasor_values['P'] = self.phasor_plot.addLine(
            x=0,
            pen=pg.mkPen(color='g', width=2, style=Qt.DotLine))
        # self.phasor_values['Q'] = self.phasor_plot.canvas.axes.axhline(
        #     color='c', zorder=32, lw=1, ls='--')

    def init_sinewave_plot(self):
        xmin = -180  # graden
        xmax = 540  # graden
        ymin = -2
        ymax = 2

        self.sinewave_plot.setTitle('Waveforms')
        self.sinewave_plot.setLabel('bottom', text='Angle', units='degree')
        self.sinewave_plot.setLabel('left', text='Value', units='p.u.')
        self.sinewave_plot.showGrid(x=True, y=True)
        self.sinewave_plot.getAxis('bottom').setTickSpacing(major=90, minor=30)
        self.sinewave_plot.getAxis('left').setTickSpacing(major=1, minor=.1)
        self.sinewave_plot.addLegend(offset=[30, -30])
        self.sinewave_plot.disableAutoRange()
        self.sinewave_plot.setYRange(min=ymin, max=ymax, padding=0)
        self.sinewave_plot.setXRange(min=xmin, max=xmax)

        self.sinewave_plot.addLine(
            x=0,
            pen=pg.mkPen('w', width=2, style=Qt.DashLine),
            z=-1,
            )
        self.sinewave_plot.addLine(
            y=0,
            pen=pg.mkPen('w', width=2, style=Qt.DashLine),
            z=-1,
            )

        x_range = self.sinewave_plot.getAxis('bottom').range
        self.deg_range = np.arange(x_range[0], x_range[1], step=1)
        # self.phi = np.arange(-np.pi, 3*np.pi, 4*np.pi/1000)
        self.phi_range = self.deg_range/180*np.pi
        # self.deg = self.phi/np.pi*180

        self.sinewave_lines = {}
        self.sinewave_lines['U'] = self.sinewave_plot.plot(
            pen=pg.mkPen('b', width=2),
            name='U',
            )
        self.sinewave_lines['I'] = self.sinewave_plot.plot(
            pen=pg.mkPen('r', width=2),
            name='I',
             )
        self.sinewave_lines['S'] = self.sinewave_plot.plot(
            pen=pg.mkPen('g', width=2),
            name='P',
            )

        # # self.sinewave_lines['P'], = self.sinewave_plot.canvas.axes.plot(
        # #    self.phi, np.zeros(len(self.phi)), 'g', zorder=41)
        # # self.sinewave_lines['Q'], = self.sinewave_plot.canvas.axes.plot(
        # #    self.phi, np.zeros(len(self.phi)), 'm', zorder=51)

        self.sinewave_valuelines = {}
        self.sinewave_valuelines['U'] = self.sinewave_plot.addLine(
            y=0,
            pen=pg.mkPen('b', width=2, style=Qt.DotLine),
            )
        self.sinewave_valuelines['I'] = self.sinewave_plot.addLine(
            y=0,
            pen=pg.mkPen('r', width=2, style=Qt.DotLine),
            )
        self.sinewave_valuelines['S'] = self.sinewave_plot.addLine(
            y=0,
            pen=pg.mkPen('g', width=2, style=Qt.DotLine),
            )

    def update_calculations(self):
        self.Ucomplex = self.U()
        self.Icomplex = self.I()
        self.S0complex = self.S0()
        self.S1complex = self.S1()
        self.Scomplex = self.S()

    def update_plots(self):
        # plot phasor lines
        self.phasor_lines['U'].setData(
            y=[0, np.imag(self.Ucomplex)],
            x=[0, np.real(self.Ucomplex)],
            )

        self.phasor_lines['I'].setData(
            y=[0, np.imag(self.Icomplex)],
            x=[0, np.real(self.Icomplex)],
            )

        self.phasor_lines['S'].setData(
            y=[np.imag(self.S0complex), np.imag(self.Scomplex)],
            x=[np.real(self.S0complex), np.real(self.Scomplex)],
            )

        # self.phasor_lines['Q'].set_ydata([0,np.imag(S1())])
        # self.phasor_lines['P'].set_xdata([0,np.real(S1())])

        # plot phasor circles
        phi_circle = np.arange(0, 2*np.pi, np.pi/180)

        Ucircle = self.U(phi=phi_circle)
        self.phasor_circles['U'].setData(
            x=np.real(Ucircle),
            y=np.imag(Ucircle),
            )

        Icircle = self.I(phi=phi_circle)
        self.phasor_circles['I'].setData(
            x=np.real(Icircle),
            y=np.imag(Icircle),
            )

        Scircle = self.S(phi=phi_circle/2)
        self.phasor_circles['S'].setData(
            x=np.real(Scircle),
            y=np.imag(Scircle),
            )

        # plot phasor values
        self.phasor_values['U'].setValue(
            v=np.real(self.Ucomplex),
            )
        self.phasor_values['I'].setValue(
            v=np.real(self.Icomplex),
            )
        self.phasor_values['P'].setValue(
            v=np.real(self.Scomplex),
            )
        # self.phasor_values['Q'].set_ydata(np.imag(S(inst_phi_rad))*np.ones(2))

        # update sinewave lines
        phi_realtime = self.phi_range + self.inst_phi_rad

        Urealtime = np.real(self.U(phi=phi_realtime))
        self.sinewave_lines['U'].setData(
            x=self.deg_range,
            y=Urealtime,
            )

        Irealtime = np.real(self.I(phi=phi_realtime))
        self.sinewave_lines['I'].setData(
            x=self.deg_range,
            y=Irealtime,
            )

        Srealtime = np.real(self.S(phi=phi_realtime))
        self.sinewave_lines['S'].setData(
            x=self.deg_range,
            y=Srealtime,
            )
        # self.sinewave_lines['P'].set_ydata(np.)

        # update sinewave timelines
        # self.sinewave_timelines[-1].set_xdata(
        #     (inst_phi_rad-2*np.pi)*np.ones(2))
        # self.sinewave_timelines[0].set_xdata(
        #     (inst_phi_rad)*np.ones(2))
        # self.sinewave_timelines[1].set_xdata(
        #     (inst_phi_rad+2*np.pi)*np.ones(2))

        self.sinewave_valuelines['U'].setValue(
            v=np.real(self.Ucomplex),
            )
        self.sinewave_valuelines['I'].setValue(
            v=np.real(self.Icomplex),
            )
        self.sinewave_valuelines['S'].setValue(
            v=np.real(self.Scomplex),
            )

    def set_instantaneous_phase(self, phase=0):
        self.instantaneous_phase_angle.setValue(phase+90)

    def increment_instantaneous_phase(self):
        self.instantaneous_phase_angle.setValue(
            self.instantaneous_phase_angle.value()+1)


def main():
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    window = PowerPlotApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
