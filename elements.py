from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import laser as ls


port = '/dev/ttyUSB0'
freq = None

def connect_to_laser():
    if port == 'exit':
        return port
    try:
        global trig, laser_on, laser
        laser = ls.Laser(port, debug_flag=False)
        trig = laser.get_trig()
        laser_on = laser.is_pumping_on()
        return True
    except:
        return False


class PowerWindow(QtWidgets.QGridLayout):

    def __init__(self):

        super().__init__()
        self._initUI()

    def _initUI(self):
        self.power_energy_checkbox = QtWidgets.QButtonGroup(self)
        self.power_button = QtWidgets.QRadioButton('Power [mW]')
        self.energy_button = QtWidgets.QRadioButton('Energy [mkJ]')
        self.power_energy_checkbox.addButton(self.power_button)
        self.power_energy_checkbox.addButton(self.energy_button)

        self.addWidget(self.power_button, 0, 0)
        self.addWidget(self.energy_button, 0, 1)
        self.energy_button.setChecked(True)

        self.power_display = QtWidgets.QLCDNumber()
        self.addWidget(self.power_display, 1, 0, 1, 2)

        self.power_percent_label = QtWidgets.QLabel('Pumping power: not init')
        self.addWidget(self.power_percent_label, 2, 0, 1, 2)

        self.power_scroll = QtWidgets.QScrollBar(Qt.Horizontal)
        self.power_scroll.setMaximum(100)
        self.power_scroll.singleStep = 1
        self.power_scroll.valueChanged.connect(self.scroll)
        self.addWidget(self.power_scroll, 3, 0, 1, 2)

    def information_update(self):
        if trig == 'ext':
            self.energy_button.setChecked(True)
        energy = laser.get_energy()
        if self.energy_button.isChecked():
            self.power_display.display(str(float(energy)))
        else:
            self.power_display.display(energy * freq / 1000)

    def scroll(self):
        laser.set_power(self.power_scroll.value())
        self.power_percent_label.setText('Pumping power: {} %'.format(self.power_scroll.value()))


class PumpingWindow(QtWidgets.QGridLayout):

    def __init__(self):

        super().__init__()
        self._initUI()

    def _initUI(self):
        self.text = QtWidgets.QLabel("Pumping")
        self.addWidget(self.text, 0, 0)

        self.on_off = QtWidgets.QButtonGroup(self)
        self.on = QtWidgets.QRadioButton('On')
        self.off = QtWidgets.QRadioButton('Off')

        self.on_off.addButton(self.on)
        self.on_off.addButton(self.off)

        self.on.clicked.connect(self.turn_on)
        self.off.clicked.connect(self.turn_off)

        self.addWidget(self.on, 0, 1)
        self.addWidget(self.off, 0, 2)

    def turn_off(self):
        laser.off()

    def turn_on(self):
        laser.on()

    def information_update(self):
        self.on.blockSignals(True)
        if laser_on:
            self.on.setChecked(True)
        else:
            self.off.setChecked(True)
        self.on.blockSignals(False)


class StatusWindow(QtWidgets.QGridLayout):

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.system_status = QtWidgets.QGroupBox("System Status")
        self.pumping_text = QtWidgets.QLabel('Pumping')
        self.rf_cabel_text = QtWidgets.QLabel('RF cabel')
        self.rf_cabel_text.setToolTip('Подключение радиочастотного кабеля')

        self.ld_temp_text = QtWidgets.QLabel('LD °t')
        self.ld_temp_text.setToolTip('Температура лазерных диодов')
        self.psu_temp_text = QtWidgets.QLabel('PSU °t')
        self.psu_temp_text.setToolTip('Температура блока питания')
        self.lh_case_temp_text = QtWidgets.QLabel('LH Case °t')
        self.lh_case_temp_text.setToolTip('Температура основания лазера')
        self.triggering_text = QtWidgets.QLabel('Triggering')
        self.triggering_text.setToolTip('Тип запуска')

        self.addWidget(self.system_status, 1, 0)
        self.addWidget(self.pumping_text, 2, 0)
        self.addWidget(self.rf_cabel_text, 3, 0)
        self.addWidget(self.ld_temp_text, 4, 0)
        self.addWidget(self.psu_temp_text, 5, 0)
        self.addWidget(self.lh_case_temp_text, 6, 0)
        self.addWidget(self.triggering_text, 7, 0)

    def information_update(self):
        # TODO: обработка отключенного лазера
        global laser_on
        if laser.is_pumping_on():
            laser_on = True
            self.pumping_text.setText('Pumping: On')
        else:
            self.pumping_text.setText('Pumping: Off')
            laser_on = False

        if laser.check_rf_cable():
            self.rf_cabel_text.setText('RF cabel: connect')
            self.rf_cabel_text.setStyleSheet('color: green')
        else:
            self.rf_cabel_text.setText('RF cabel: DISCONNECT')
            self.rf_cabel_text.setStyleSheet('color: red')

        global trig
        trig = laser.get_trig()
        if trig == 'int':
            self.triggering_text.setText('Triggering: internal')
        elif trig == 'ext':
            self.triggering_text.setText('Triggering: external')
        else:
            self.triggering_text.setText('Triggering: can\'t read')

        ld_temp, lh_case_temp, psu_temp = laser.check_temperature()
        if ld_temp:
            self.ld_temp_text.setText('LD °t: normal')
            self.ld_temp_text.setStyleSheet('color: green')
        else:
            self.ld_temp_text.setText('LD °t: overheat')
            self.ld_temp_text.setStyleSheet('color: red')
        if lh_case_temp:
            self.lh_case_temp_text.setText('LH Case °t: normal')
            self.lh_case_temp_text.setStyleSheet('color: green')
        else:
            self.lh_case_temp_text.setText('LH Case °t: overheat')
            self.lh_case_temp_text.setStyleSheet('color: red')
        if psu_temp:
            self.psu_temp_text.setText('PSU °t: normal')
            self.psu_temp_text.setStyleSheet('color: green')
        else:
            self.psu_temp_text.setText('PSU °t: overheat')
            self.psu_temp_text.setStyleSheet('color: red')


class FrequencyWindow(QtWidgets.QGridLayout):

    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.checkbox = QtWidgets.QButtonGroup(self)
        self.internal = QtWidgets.QRadioButton('Internal')
        self.external = QtWidgets.QRadioButton('External')
        self.checkbox.addButton(self.internal)
        self.checkbox.addButton(self.external)

        self.internal.clicked.connect(self.set_internal)
        self.external.clicked.connect(self.set_external)
        self.addWidget(self.internal, 0, 0)
        self.addWidget(self.external, 0, 1)

        self.freq_display = QtWidgets.QLCDNumber()
        self.addWidget(self.freq_display, 1, 0, 1, 2)

        self.label = QtWidgets.QLabel('Set frequency [Hz]')
        self.addWidget(self.label, 2, 0, 1, 2)

        self.scroll = QtWidgets.QScrollBar(Qt.Horizontal)
        self.scroll.setMaximum(400)
        self.scroll.setMinimum(80)
        self.scroll.valueChanged.connect(self.information_update)
        self.addWidget(self.scroll, 3, 0, 1, 2)

    def information_update(self):
        if trig == 'int':
            global freq
            freq = self.scroll.value() * 10
            laser.set_freq(freq)
            self.freq_display.display(freq)
            self.internal.setChecked(True)
        else:
            self.freq_display.display('---')
            self.external.setChecked(True)

    def set_internal(self):
        laser.set_trig('int')

    def set_external(self):
        laser.set_trig('ext')


class DeviceWindow(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select device")
        self.setFixedSize(200, 200)

        global port
        port = 'exit'

        layout = QtWidgets.QVBoxLayout(self)
        self.qlist = QtWidgets.QListWidget()
        for i in range(6):
            self.qlist.addItem('/dev/ttyUSB' + str(i))
        layout.addWidget(self.qlist)
        self.qlist.clicked.connect(self.exit)
        # self.setWindowModality(Qt.ApplicationModal)
        self.exec_()

    def exit(self):
        global port
        port = self.qlist.currentItem().text()
        self.close()
