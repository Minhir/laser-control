import sys
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget, QToolTip
from PyQt5.QtCore import QTimer
import elements


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Laser control")
        self.timer = QTimer(self)
        self.widget = QWidget()
        self.setFixedSize(600, 200)
        self.setCentralWidget(self.widget)

        self.power_widget = elements.PowerWindow()
        self.pumping_widget = elements.PumpingWindow()
        self.status_widget = elements.StatusWindow()
        self.frequency_widget = elements.FrequencyWindow()

        self.select_port()

        self.initUI()
        self.init_timer()
        self.show()

    def select_port(self):
        while True:
            ctl = elements.connect_to_laser()
            if ctl is True:
                break
            elif ctl == 'exit':
                sys.exit()
            else:
                elements.DeviceWindow()

    def initUI(self):
        window_layout = QGridLayout(self.widget)
        window_layout.addLayout(self.pumping_widget, 0, 0, 1, 1)
        window_layout.addLayout(self.power_widget, 0, 1, 2, 1)
        window_layout.addLayout(self.frequency_widget, 0, 2, 2, 1)
        window_layout.addLayout(self.status_widget, 1, 0, 1, 1)

    def init_timer(self):
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.status_widget.information_update)
        self.timer.timeout.connect(self.power_widget.information_update)
        self.timer.timeout.connect(self.frequency_widget.information_update)
        self.timer.timeout.connect(self.pumping_widget.information_update)
        self.timer.start()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
