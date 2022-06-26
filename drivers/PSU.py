import serial
import time

SERIAL_WAIT = 0.2
DEFAULT_VOLTAGES = (1.0, 1.0, 1.0)
DEFAULT_MAX_CURRENTS = (0.1, 0.1, 0.1)
DEFAULT_PORT = 'COM28'
DEFAULT_BAUD_RATE = 9600


class PSU:
    def __init__(self, port=DEFAULT_PORT,
                 baud_rate=DEFAULT_BAUD_RATE,
                 voltages=DEFAULT_VOLTAGES,
                 max_currents=DEFAULT_MAX_CURRENTS):
        """
        creates object for PSU control and communication
        Args:
            port (): String, port name, where PSU is connected, 'COM1' for example
            baud_rate (): int number, 38400 for example
            voltages (): output voltage for PSU channels, expected tuple or list with 1, 2 or 3 elements
            max_currents (): current limits for PSU channels, expected tuple or list with 1, 2 or 3 elements
        """
        self.channel_volt = list(voltages)
        self.channel_max_current = list(max_currents)
        self.serial = serial.Serial(port=port,
                                    baudrate=baud_rate,
                                    timeout=0.5)
        time.sleep(0.5)
        self.set_voltage()
        self.set_max_current()

    def set_max_current(self, max_currents=None):
        """
        sets current limits in PSU channels
        Args:
            max_currents (): current limit for PSU channels, could be 1, 2 or 3 elements list, if not specified,
            actual values are used, otherwise values are updated
        """
        if max_currents:
            self.channel_max_current = list(max_currents)
        for i, max_current in enumerate(self.channel_max_current):
            self.serial.write(':CHAN{:d}:CURR {:.3f}\n'.format(i + 1, max_current).encode())
            time.sleep(SERIAL_WAIT)

    def set_voltage(self, voltages=None):
        """
        sets output voltage in PSU channels
        Args:
            voltages (): voltage for PSU channels, could be 1, 2 or 3 element list, if not specified,
            actual values are used, otherwise values are updated
        """
        if voltages:
            self.channel_volt = list(voltages)
        for i, voltage in enumerate(self.channel_volt):
            self.serial.write(':CHAN{:d}:VOLT {:.3f}\n'.format(i + 1, voltage).encode())
            time.sleep(SERIAL_WAIT)

    def get_voltage(self):
        """
        measure actual voltage in PSU channels
        Returns:
            @voltages: list with actual voltage in PSU channels
        """
        voltages = []
        self.serial.read(self.serial.inWaiting())
        for i, _ in enumerate(self.channel_volt):
            self.serial.write(':CHAN{:d}:MEAS:VOLT?\n'.format(i + 1).encode())
            time.sleep(SERIAL_WAIT)
            volt = self.serial.read(self.serial.inWaiting())

            voltages.append(float(volt.decode()))
        return voltages

    def get_currents(self):
        """
        measure actual current consumption in PSU channels
        Returns:
            @currents: list with actual currents in PSU channels
        """
        currents = []
        self.serial.read(self.serial.inWaiting())
        for i, _ in enumerate(self.channel_volt):
            self.serial.write(':CHAN{:d}:MEAS:CURR?\n'.format(i + 1).encode())
            time.sleep(SERIAL_WAIT)
            curr = self.serial.read(self.serial.inWaiting())
            currents.append(float(curr.decode()))
        return currents

    def on(self):
        self.serial.write(':OUTP:STAT 1\n'.encode())
        time.sleep(SERIAL_WAIT)

    def off(self):
        self.serial.write(':OUTP:STAT 0\n'.encode())
        time.sleep(SERIAL_WAIT)

    def __del__(self):
        self.serial.close()


if __name__ == '__main__':
    print('PSU test')
    psu = PSU()
    psu.on()
    print(psu.get_voltage(), psu.get_currents())
    psu.off()
    del psu
    print('Done!')
