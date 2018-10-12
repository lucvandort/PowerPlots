import sys
import time
import numpy as np
import pyqtgraph as pg

from PyQt5 import uic
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

# Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')


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

    def __init__(self):
        super(PowerPlotApp, self).__init__()
        uic.loadUi('powerplots.ui', self)
        self.show()

        self.init_phasor_plot()
        self.init_sinewave_plot()
        self.update_plots()

        self.voltage_amplitude.valueChanged.connect(self.update_plots)
        self.voltage_phase_angle.valueChanged.connect(self.update_plots)
        self.current_amplitude.valueChanged.connect(self.update_plots)
        self.current_phase_angle.valueChanged.connect(self.update_plots)
        self.instantaneous_phase_angle.valueChanged.connect(self.update_plots)

        self.playback_button.clicked.connect(self.start_playback)
        self.playback_reset_button.clicked.connect(
            self.set_instantaneous_phase)

    def start_playback(self):
        self.playback_reset_button.setEnabled(False)
        self.instantaneous_phase_angle.setEnabled(False)
        self.playback_button.setText('Pause')
        self.playback_button.clicked.disconnect(self.start_playback)
        self.playback_button.clicked.connect(self.stop_playback)

        self.playback_thread = playbackThread()
        self.playback_thread.sig_step.connect(
            self.increment_instantaneous_phase)
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

        self.phasor_plot.showGrid(x=True, y=True)
        self.phasor_plot.disableAutoRange()
        self.phasor_plot.setYRange(min=ymin, max=ymax, padding=0)
        self.phasor_plot.setXRange(min=xmin, max=xmax, padding=0)

        # self.phasor_plot.canvas.axes.axhline(color='black', zorder=1, lw=1)
        # self.phasor_plot.canvas.axes.axvline(color='black', zorder=1, lw=1)
        # unity_circle = np.exp(-1j*np.arange(0, 2*np.pi, np.pi/180))
        # self.phasor_plot.canvas.axes.plot(
        #     np.real(unity_circle),
        #     np.imag(unity_circle), '0.2', zorder=-1, lw=1)

        self.phasor_lines = {}
        self.phasor_lines['U'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='b', width=2))
        self.phasor_lines['I'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='r', width=2))
        self.phasor_lines['S'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='g', width=2))

        self.phasor_circles = {}
        self.phasor_circles['U'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='b', width=1))
        self.phasor_circles['I'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='r', width=1))
        self.phasor_circles['S'] = self.phasor_plot.plot(
            pen=pg.mkPen(color='g', width=1))

        self.phasor_values = {}
        self.phasor_values['U'] = self.phasor_plot.plot(
            y=np.array([ymin, ymax]),
            pen=pg.mkPen(color='b', width=1, style=Qt.DashLine))
        self.phasor_values['I'] = self.phasor_plot.plot(
            y=np.array([ymin, ymax]),
            pen=pg.mkPen(color='r', width=1, style=Qt.DashLine))
        self.phasor_values['P'] = self.phasor_plot.plot(
            y=np.array([ymin, ymax]),
            pen=pg.mkPen(color='g', width=1, style=Qt.DashLine))
        # self.phasor_values['Q'] = self.phasor_plot.canvas.axes.axhline(
        #     color='c', zorder=32, lw=1, ls='--')

    def init_sinewave_plot(self):
        xmin = -np.pi
        xmax = 3*np.pi
        ymin = -2
        ymax = 2

        self.sinewave_plot.showGrid(x=True, y=True)
        self.sinewave_plot.disableAutoRange()
        self.sinewave_plot.setYRange(min=ymin, max=ymax, padding=0)
        self.sinewave_plot.setXRange(min=xmin, max=xmax, padding=0)

        self.phi = np.arange(-np.pi, 3*np.pi, 4*np.pi/1000)

        self.sinewave_lines = {}
        self.sinewave_lines['U'] = self.sinewave_plot.plot(
            pen=pg.mkPen('b', width=2))
        self.sinewave_lines['I'] = self.sinewave_plot.plot(
            pen=pg.mkPen('r', width=2))
        self.sinewave_lines['S'] = self.sinewave_plot.plot(
            pen=pg.mkPen('g', width=2))

        # # self.sinewave_lines['P'], = self.sinewave_plot.canvas.axes.plot(
        # #    self.phi, np.zeros(len(self.phi)), 'g', zorder=41)
        # # self.sinewave_lines['Q'], = self.sinewave_plot.canvas.axes.plot(
        # #    self.phi, np.zeros(len(self.phi)), 'm', zorder=51)

        self.sinewave_valuelines = {}
        self.sinewave_valuelines['U'] = self.sinewave_plot.plot(
            x=np.array([xmin, xmax]),
            pen=pg.mkPen('b', width=1, style=Qt.DashLine))
        self.sinewave_valuelines['I'] = self.sinewave_plot.plot(
            x=np.array([xmin, xmax]),
            pen=pg.mkPen('r', width=1, style=Qt.DashLine))
        self.sinewave_valuelines['S'] = self.sinewave_plot.plot(
            x=np.array([xmin, xmax]),
            pen=pg.mkPen('g', width=1, style=Qt.DashLine))

    def update_plots(self, inst_phi=0):
        U0 = self.voltage_amplitude.value()/100
        Uangle = self.voltage_phase_angle.value()/180*np.pi
        I0 = self.current_amplitude.value()/100
        Iangle = self.current_phase_angle.value()/180*np.pi

        def U(phi=0):
            return U0 * np.exp(1j*Uangle) * np.exp(1j*phi)

        def I(phi=0):
            return I0 * np.exp(1j*Iangle) * np.exp(1j*phi)

        def S1(phi=0):
            return U(phi=phi) * I(phi=phi)

        def S0(phi=0):
            return U(phi=phi) * np.conj(I(phi=phi))

        def S(phi=0):
            return S0(phi=phi) + S1(phi=phi)

        inst_phi_deg = self.instantaneous_phase_angle.value() - 90
        inst_phi_rad = inst_phi_deg / 180 * np.pi
        self.instantaneous_phase_display.display(inst_phi_deg)

        # plot phasor lines
        self.phasor_lines['U'].setData(
            y=[0, np.imag(U(inst_phi_rad))],
            x=[0, np.real(U(inst_phi_rad))])
        self.phasor_lines['I'].setData(
            y=[0, np.imag(I(inst_phi_rad))],
            x=[0, np.real(I(inst_phi_rad))])
        self.phasor_lines['S'].setData(
            y=[np.imag(S0(inst_phi_rad)), np.imag(S(inst_phi_rad))],
            x=[np.real(S0(inst_phi_rad)), np.real(S(inst_phi_rad))])
        # self.phasor_lines['Q'].set_ydata([0,np.imag(S1())])
        # self.phasor_lines['P'].set_xdata([0,np.real(S1())])

        # plot phasor circles
        self.phasor_circles['U'].setData(
            x=np.real(U(np.arange(0, 2*np.pi, np.pi/180))),
            y=np.imag(U(np.arange(0, 2*np.pi, np.pi/180))))
        self.phasor_circles['I'].setData(
            x=np.real(I(np.arange(0, 2*np.pi, np.pi/180))),
            y=np.imag(I(np.arange(0, 2*np.pi, np.pi/180))))
        self.phasor_circles['S'].setData(
            x=np.real(S(np.arange(0, 2*np.pi, np.pi/180))),
            y=np.imag(S(np.arange(0, 2*np.pi, np.pi/180))))

        # plot phasor values
        self.phasor_values['U'].setData(
            x=np.real(U(inst_phi_rad))*np.ones(2),
            y=self.phasor_values['U'].yData)
        self.phasor_values['I'].setData(
            x=np.real(I(inst_phi_rad))*np.ones(2),
            y=self.phasor_values['I'].yData)
        self.phasor_values['P'].setData(
            x=np.real(S(inst_phi_rad))*np.ones(2),
            y=self.phasor_values['P'].yData)
        # self.phasor_values['Q'].set_ydata(np.imag(S(inst_phi_rad))*np.ones(2))

        # update sinewave lines
        self.sinewave_lines['U'].setData(
            x=self.phi, y=np.real(U(self.phi + inst_phi_rad)))
        self.sinewave_lines['I'].setData(
            x=self.phi, y=np.real(I(self.phi + inst_phi_rad)))
        self.sinewave_lines['S'].setData(
            x=self.phi, y=np.real(S(self.phi + inst_phi_rad)))
        # self.sinewave_lines['P'].set_ydata(np.)

        # update sinewave timelines
        # self.sinewave_timelines[-1].set_xdata(
        #     (inst_phi_rad-2*np.pi)*np.ones(2))
        # self.sinewave_timelines[0].set_xdata(
        #     (inst_phi_rad)*np.ones(2))
        # self.sinewave_timelines[1].set_xdata(
        #     (inst_phi_rad+2*np.pi)*np.ones(2))

        self.sinewave_valuelines['U'].setData(
            x=self.sinewave_valuelines['U'].xData,
            y=np.real(U(inst_phi_rad))*np.ones(2))
        self.sinewave_valuelines['I'].setData(
            x=self.sinewave_valuelines['I'].xData,
            y=np.real(I(inst_phi_rad))*np.ones(2))
        self.sinewave_valuelines['S'].setData(
            x=self.sinewave_valuelines['S'].xData,
            y=np.real(S(inst_phi_rad))*np.ones(2))

    def set_instantaneous_phase(self, phase=0):
        self.instantaneous_phase_angle.setValue(phase+90)

    def increment_instantaneous_phase(self):
        self.instantaneous_phase_angle.setValue(
            self.instantaneous_phase_angle.value()+1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PowerPlotApp()
    sys.exit(app.exec_())
