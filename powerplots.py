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
        self.instantaneous_phase_angle.valueChanged.connect(self.update_plots)

        # self.playback_button.clicked.connect(self.)
        self.playback_reset_button.clicked.connect(self.reset_instantaneous_phase)

    def init_phasor_plot(self):
        self.phasor_plot.canvas.axes.set_ylim([-2,2])
        self.phasor_plot.canvas.axes.set_xlim([-2,2])
        self.phasor_plot.canvas.axes.grid(True)
        self.phasor_plot.canvas.axes.axis('equal')
        
        self.phasor_plot.canvas.axes.axhline(color='black', zorder=1, lw=1)
        self.phasor_plot.canvas.axes.axvline(color='black', zorder=1, lw=1)
        unity_circle = np.exp(-1j*np.arange(0,2*np.pi,np.pi/180))
        self.phasor_plot.canvas.axes.plot(np.real(unity_circle), np.imag(unity_circle), '0.2', zorder=-1, lw=1)

        self.phasor_lines = {}
        self.phasor_lines['U'], = self.phasor_plot.canvas.axes.plot([0,0],[0,0], 'b', zorder=10, lw=3)
        self.phasor_lines['I'], = self.phasor_plot.canvas.axes.plot([0,0],[0,0], 'r', zorder=20, lw=3)
        self.phasor_lines['S'], = self.phasor_plot.canvas.axes.plot([0,0],[0,0], 'c', zorder=30, lw=3)

        self.phasor_circles = {}
        self.phasor_circles['U'], = self.phasor_plot.canvas.axes.plot(np.zeros(360), np.zeros(360), 'b', zorder=2, lw=1, ls='--')
        self.phasor_circles['I'], = self.phasor_plot.canvas.axes.plot(np.zeros(360), np.zeros(360), 'r', zorder=3, lw=1, ls='--')
        self.phasor_circles['S'], = self.phasor_plot.canvas.axes.plot(np.zeros(360), np.zeros(360), 'c', zorder=4, lw=1, ls='--')

        self.phasor_values = {}
        self.phasor_values['U'] = self.phasor_plot.canvas.axes.axvline(color='b', zorder=11, lw=1, ls='--')
        self.phasor_values['I'] = self.phasor_plot.canvas.axes.axvline(color='r', zorder=21, lw=1, ls='--')
        self.phasor_values['P'] = self.phasor_plot.canvas.axes.axvline(color='c', zorder=31, lw=1, ls='--')
        self.phasor_values['Q'] = self.phasor_plot.canvas.axes.axhline(color='c', zorder=32, lw=1, ls='--')

    def init_sinewave_plot(self):
        self.sinewave_plot.canvas.axes.set_ylim([-2,2])
        self.sinewave_plot.canvas.axes.set_xlim([-np.pi,3*np.pi])
        self.sinewave_plot.canvas.axes.grid(True)
        
        self.sinewave_timelines = {}
        self.sinewave_timelines[-1] = self.sinewave_plot.canvas.axes.axvline(x=-2*np.pi, color='black', zorder=1, lw=1, ls='--')
        self.sinewave_timelines[0] = self.sinewave_plot.canvas.axes.axvline(x=0, color='black', zorder=1, lw=1, ls='--')
        self.sinewave_timelines[1] = self.sinewave_plot.canvas.axes.axvline(x=2*np.pi, color='black', zorder=1, lw=1, ls='--')

        self.phi = np.arange(-np.pi,3*np.pi,4*np.pi/1000)

        self.sinewave_lines = {}
        self.sinewave_lines['U'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'b', zorder=11)
        self.sinewave_lines['I'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'r', zorder=21)
        self.sinewave_lines['S'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'c', zorder=31)
        # self.sinewave_lines['P'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'g', zorder=41)
        # self.sinewave_lines['Q'], = self.sinewave_plot.canvas.axes.plot(self.phi, np.zeros(len(self.phi)), 'm', zorder=51)

    def update_plots(self, inst_phi=0):
        U = lambda phi=0: self.voltage_amplitude.value()/100 * np.exp(1j * self.voltage_phase_angle.value()/180*np.pi) * np.exp(1j*phi)
        I = lambda phi=0: self.current_amplitude.value()/100 * np.exp(1j * self.current_phase_angle.value()/180*np.pi) * np.exp(1j*phi)
        S1 = lambda phi=0: U(phi) * I(phi)
        S0 = lambda phi=0: U(phi) * np.conj(I(phi))
        S = lambda phi=0: S0(phi) + S1(phi)

        inst_phi_deg = self.instantaneous_phase_angle.value() - 90
        inst_phi_rad = inst_phi_deg / 180 * np.pi
        self.instantaneous_phase_display.display(inst_phi_deg)
    
        # plot phasor lines
        self.phasor_lines['U'].set_ydata([0,np.imag(U(inst_phi_rad))])
        self.phasor_lines['U'].set_xdata([0,np.real(U(inst_phi_rad))])
        self.phasor_lines['I'].set_ydata([0,np.imag(I(inst_phi_rad))])
        self.phasor_lines['I'].set_xdata([0,np.real(I(inst_phi_rad))])
        self.phasor_lines['S'].set_ydata([np.imag(S0(inst_phi_rad)),np.imag(S(inst_phi_rad))])
        self.phasor_lines['S'].set_xdata([np.real(S0(inst_phi_rad)),np.real(S(inst_phi_rad))])
        # self.phasor_lines['Q'].set_ydata([0,np.imag(S1())])
        # self.phasor_lines['P'].set_xdata([0,np.real(S1())])

        # plot phasor circles
        self.phasor_circles['U'].set_xdata(np.real(U(np.arange(0,2*np.pi,np.pi/180))))
        self.phasor_circles['U'].set_ydata(np.imag(U(np.arange(0,2*np.pi,np.pi/180))))
        self.phasor_circles['I'].set_xdata(np.real(I(np.arange(0,2*np.pi,np.pi/180))))
        self.phasor_circles['I'].set_ydata(np.imag(I(np.arange(0,2*np.pi,np.pi/180))))
        self.phasor_circles['S'].set_xdata(np.real(S(np.arange(0,2*np.pi,np.pi/180))))
        self.phasor_circles['S'].set_ydata(np.imag(S(np.arange(0,2*np.pi,np.pi/180))))

        # plot phasor values
        self.phasor_values['U'].set_xdata(np.real(U(inst_phi_rad))*np.ones(2))
        self.phasor_values['I'].set_xdata(np.real(I(inst_phi_rad))*np.ones(2))
        self.phasor_values['P'].set_xdata(np.real(S(inst_phi_rad))*np.ones(2))
        self.phasor_values['Q'].set_ydata(np.imag(S(inst_phi_rad))*np.ones(2))



        # refresh phasor plot
        self.phasor_plot.canvas.draw()
        self.phasor_plot.canvas.flush_events()


        # update sinewave liens
        self.sinewave_lines['U'].set_ydata(np.real(U(self.phi)))
        self.sinewave_lines['I'].set_ydata(np.real(I(self.phi)))
        self.sinewave_lines['S'].set_ydata(np.real(S(self.phi)))
        # self.sinewave_lines['P'].set_ydata(np.)

        # update sinewave timelines
        self.sinewave_timelines[-1].set_xdata((inst_phi_rad-2*np.pi)*np.ones(2))
        self.sinewave_timelines[0].set_xdata((inst_phi_rad)*np.ones(2))
        self.sinewave_timelines[1].set_xdata((inst_phi_rad+2*np.pi)*np.ones(2))

        self.sinewave_plot.canvas.draw()
        self.sinewave_plot.canvas.flush_events()


    def reset_instantaneous_phase(self):
        self.instantaneous_phase_angle.setValue(90)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PowerPlotApp()
    sys.exit(app.exec_())
