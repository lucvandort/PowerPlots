import sys
import numpy as np
import matplotlib as mpl

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout

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

    def init_phasor_plot(self):
        self.phasor_plot.canvas.axes.set_ylim([-2,2])
        self.phasor_plot.canvas.axes.set_xlim([-2,2])
        self.phasor_plot.canvas.axes.grid(True)
        
        circle = np.exp(-1j*np.arange(0,2*np.pi,np.pi/180))
        self.phasor_plot.canvas.axes.plot(np.real(circle), np.imag(circle), '0.5', lw=1)

        self.phasor_lines = {}
        self.phasor_lines['U'], = self.phasor_plot.canvas.axes.plot([0,0],[0,0], 'b', zorder=1, lw=3)
        self.phasor_lines['I'], = self.phasor_plot.canvas.axes.plot([0,0],[0,0], 'r', zorder=2, lw=3)
        self.phasor_lines['S'], = self.phasor_plot.canvas.axes.plot([0,0],[0,0], 'c', zorder=3, lw=3)
        self.phasor_lines['P'], = self.phasor_plot.canvas.axes.plot([0,0],[0,0], 'g', zorder=4, lw=1, ls='--')
        self.phasor_lines['Q'], = self.phasor_plot.canvas.axes.plot([0,0],[0,0], 'm', zorder=5, lw=1, ls='--')

    def init_sinewave_plot(self):
        self.sinewave_plot.canvas.axes.set_ylim([-2,2])
        self.sinewave_plot.canvas.axes.set_xlim([0,4*np.pi])
        self.sinewave_plot.canvas.axes.grid(True)
        
        self.phi = np.arange(0,4*np.pi,4*np.pi/1000)

        self.sinewave_lines = {}
        self.sinewave_lines['U'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'b', zorder=1)
        self.sinewave_lines['I'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'r', zorder=2)
        self.sinewave_lines['S'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'c', zorder=3)
        self.sinewave_lines['P'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'g', zorder=4)
        self.sinewave_lines['Q'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'm', zorder=5)

    def update_plots(self):
        U = lambda phi=0: self.voltage_amplitude.value()/100 * np.exp(1j * self.voltage_phase_angle.value()/180*np.pi) * np.exp(1j*phi)
        I = lambda phi=0: self.current_amplitude.value()/100 * np.exp(1j * self.current_phase_angle.value()/180*np.pi) * np.exp(1j*phi)
        S1 = lambda phi=0: U(phi) * I(phi)
        S0 = lambda phi=0: U(phi) * np.conj(I(phi))
    
        self.phasor_lines['U'].set_ydata([0,np.imag(U())])
        self.phasor_lines['U'].set_xdata([0,np.real(U())])
        self.phasor_lines['I'].set_ydata([0,np.imag(I())])
        self.phasor_lines['I'].set_xdata([0,np.real(I())])
        self.phasor_lines['S'].set_ydata([np.imag(S0()),np.imag(S0())+np.imag(S1())])
        self.phasor_lines['S'].set_xdata([np.real(S0()),np.real(S0())+np.real(S1())])
        self.phasor_lines['Q'].set_ydata([0,np.imag(S1())])
        self.phasor_lines['P'].set_xdata([0,np.real(S1())])

        self.phasor_plot.canvas.draw()
        self.phasor_plot.canvas.flush_events()

        self.sinewave_lines['U'].set_ydata(np.real(U(self.phi)))
        self.sinewave_lines['I'].set_ydata(np.real(I(self.phi)))
        self.sinewave_lines['S'].set_ydata(np.real(S0(self.phi)) + np.real(S1(self.phi)))
        # self.sinewave_lines['P'].set_ydata(np.)

        self.sinewave_plot.canvas.draw()
        self.sinewave_plot.canvas.flush_events()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PowerPlotApp()
    sys.exit(app.exec_())
