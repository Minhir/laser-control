import serial


class Laser:

    def __init__(self, port="/dev/ttyUSB0", debug_flag=True):
        self.debug_flag = debug_flag
        self.portN = port
        self.ser = serial.Serial(port=port,
                                 baudrate=4800,
                                 bytesize=serial.EIGHTBITS,
                                 parity=serial.PARITY_NONE,
                                 stopbits=serial.STOPBITS_ONE,
                                 write_timeout=5,
                                 timeout=5)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    def _init_state(self):
        """Для ручной инициализации только! Запись в память EEPROM."""
        self.ser.write(b'\x83')
        self.ser.write(b'\x07')

    def _read(self):
        # TODO: корректно отрабатывать timeout
        return int.from_bytes(self.ser.read(size=1), byteorder='big')

    def _debug_print(self, s):
        if self.debug_flag:
            print(s)

    def get_energy(self):
        """Усредненное показание фототока"""
        self.ser.write(b'\x08')
        a = self._read()
        self.ser.write(b'\x09')
        b = self._read()
        return (a * 256 + b) / 2  # Делим на два из показаний оф. приложения

    def set_power(self, power_percent):
        """Установка мощности (в процентах). Не сохраняется в энергонезависимой памяти"""
        power = int(power_percent * 255 / 100)
        self.ser.write(b'\x80')
        self.ser.write(power.to_bytes(1, byteorder='big'))

    def set_freq(self, freq):
        """Установка частоты в [Гц]"""
        if 800 <= freq <= 4000 and type(freq) == int:
            freq = freq // 10
        else:
            print('Недопустимая частота!')
            return
        self.ser.write(b'\x97')
        self.ser.write(int(freq % 256).to_bytes(1, byteorder='big'))
        self.ser.write(b'\x98')
        self.ser.write(int(freq // 256).to_bytes(1, byteorder='big'))

    def get_trig(self):
        self.ser.write(b'\x1E')
        n = self._read() & 1
        if n == 0:
            return 'int'
        else:
            return 'ext'

    def set_trig(self, trig):
        if trig == 'int':
            self.ser.write(b'\x9E')
            self.ser.write(b'\x00')
        elif trig == 'ext':
            self.ser.write(b'\x9E')
            self.ser.write(b'\x01')
        else:
            # TODO: сделать нормальные ошибки
            print('Trig type error')

    def on(self):
        self.ser.write(b'\x83')
        self.ser.write(b'\x01')

    def off(self):
        self.ser.write(b'\x83')
        self.ser.write(b'\x00')

    def is_pumping_on(self):
        """Флаги режима включения лазера"""
        self.ser.write(b'\x05')
        byte = self._read()
        if byte == 0:
            return False
        elif byte == 1:
            return True

    def check_rf_cable(self):
        """Проверка контакта ВЧ кабеля"""
        self.ser.write(b'\x1D')
        byte = self._read()
        if byte == 0:
            self._debug_print("Good")
            return True
        elif byte == 1:
            self._debug_print("Bad")
            return False
        else:
            self._debug_print("Unknown command")
            return False

    def check_temperature(self):
        self.ser.write(b'\x02')
        if self._read() == 1:
            self._debug_print("Температура блока накачки в порядке")
            ld_temp = True
        else:
            self._debug_print("Температура блока накачки НЕ в порядке")
            ld_temp = False

        self.ser.write(b'\x03')
        if self._read() == 1:
            self._debug_print("Температура излучателя в порядке")
            lh_case_temp = True
        else:
            self._debug_print("Температура излучателя НЕ в порядке")
            lh_case_temp = False

        self.ser.write(b'\x1F')
        if self._read() == 1:
            self._debug_print("Температура блока питания в порядке")
            psu_temp = True
        else:
            self._debug_print("Температура блока питания НЕ в порядке")
            psu_temp = False
        return ld_temp, lh_case_temp, psu_temp
