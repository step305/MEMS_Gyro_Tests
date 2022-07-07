import time
import serial

DEFAULT_PORT = 'COM10'
DEFAULT_BAUDRATE = 19200
SERIAL_WAIT = 1
CHAMBER_CHANNEL = 1


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
        self.serial.write('{:d},TEMP?\n'.format(CHAMBER_CHANNEL).encode())
        time.sleep(SERIAL_WAIT)
        resp = self.serial.read(self.serial.inWaiting()).decode().split('\n')
        resp = resp[1].split(',')
        return float(resp[0])

    def set_temperature(self, temperature):
        """
        set target temperature in chamber and run
        """
        command = '{:d},TEMP,S{:.1f}\n'.format(CHAMBER_CHANNEL, temperature)
        self.serial.write(command.encode())
        time.sleep(SERIAL_WAIT)
        command = '{:d},MODE,CONSTANT\n'.format(CHAMBER_CHANNEL)
        self.serial.write(command.encode())
        time.sleep(SERIAL_WAIT)

    def off(self):
        """
        stop chamber
        """
        command = '{:d},MODE,OFF\n'.format(CHAMBER_CHANNEL)
        self.serial.write(command.encode())
        time.sleep(SERIAL_WAIT)

    def close(self):
        """
        closes thermal chamber port
        """
        self.serial.close()


if __name__ == '__main__':
    thermal_chamber = ThermalChamber()
    print('Current temperature is {:.2f} Celsium degrees'.format(thermal_chamber.get_temperature()))
    print('Setting 40 Celsium degrees and run')
    thermal_chamber.set_temperature(temperature=40.0)
    time.sleep(15)
    print('Current temperature is {:.2f} Celsium degrees'.format(thermal_chamber.get_temperature()))
    print('Stopping chamber')
    thermal_chamber.off()
    thermal_chamber.close()
