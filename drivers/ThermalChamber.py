import time
import serial

DEFAULT_PORT = 'COM15'
DEFAULT_BAUDRATE = 9600
SERIAL_WAIT = 1


class ThermalChamber:
    def __init__(self, port=DEFAULT_PORT, baud_rate=DEFAULT_BAUDRATE):
        """
        opens chamber port and sets mode to 0 (rate)
        Args:
            port (): String, port name, ex. 'COM15'
            baud_rate (): baudrate, ex. 9600
        """
        self.serial = serial.Serial(port=port, baudrate=baud_rate, timeout=5)

    def get_temperature(self):
        """
        get current temperature in chamber
        """
        if self.serial.inWaiting() > 0:
            self.serial.read(self.serial.inWaiting())
        self.serial.write('$01I\r'.encode())
        time.sleep(SERIAL_WAIT)
        resp = self.serial.read(self.serial.inWaiting()).decode().split(' ')
        return float(resp[1])

    def set_temperature(self, temperature):
        """
        set target temperature in chamber and run
        """
        command = '$01E {:.1f} 0010.0 0000.0 0000.0 0000.0 0000.0 0010.0 ' \
                  '01010101010101010000000000000000\r'.format(temperature)
        self.serial.write(command.encode())
        time.sleep(SERIAL_WAIT)

    def off(self):
        """
        stop chamber
        """
        command = '$01E 23.0 0010.0 0000.0 0000.0 0000.0 0000.0 0010.0 00010101010101010000000000000000\r'
        self.serial.write(command.encode())
        time.sleep(SERIAL_WAIT)

    def __del__(self):
        """
        closes thermal chamber port
        """
        self.serial.close()


if __name__ == '__main__':
    thermal_chamber = ThermalChamber()
    print('Current temperature is {:.2f} Celsium degrees'.format(thermal_chamber.get_temperature()))
    print('Setting 40 Celsium degrees and run')
    thermal_chamber.set_temperature(temperature=40.0)
    time.sleep(5)
    print('Current temperature is {:.2f} Celsium degrees'.format(thermal_chamber.get_temperature()))
    print('Stopping chamber')
    thermal_chamber.off()
    del thermal_chamber
