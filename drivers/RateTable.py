import time
import serial

DEFAULT_PORT = 'COM7'
DEFAULT_BAUDRATE = 38400
SERIAL_WAIT = 0.3


class RateTable:
    def __init__(self, port=DEFAULT_PORT, baud_rate=DEFAULT_BAUDRATE):
        """
        opens rate table port and sets mode to 0 (rate)
        Args:
            port (): String, port name, ex. 'COM12'
            baud_rate (): baudrate, ex. 38400
        """
        self.serial = serial.Serial(port=port, baudrate=baud_rate, timeout=5)
        self.serial.write('OPMODE 0\r\n'.encode())
        time.sleep(SERIAL_WAIT)

    def en(self):
        """
        enables rate table motion
        """
        self.serial.write('EN\r\n'.encode())
        time.sleep(SERIAL_WAIT)

    def dis(self):
        """
        disables rate table motion
        """
        self.serial.write('DIS\r\n'.encode())
        time.sleep(SERIAL_WAIT)

    def rate(self, rate=None):
        """
        set or get rate of rate table
        Args:
            rate (): if rate is number - set rate of rate table, if omitted - get actual rate table's rate
        Returns:
            @rate: actual rate of rate table if input parameter rate is omitted
        """
        if rate or rate == 0:
            self.serial.write('J {:0.2f}\r\n'.format(rate).encode())
            time.sleep(SERIAL_WAIT * 2)
        if self.serial.inWaiting() > 0:
            self.serial.read(self.serial.inWaiting())
        self.serial.write('J\r\n'.encode())
        time.sleep(SERIAL_WAIT)
        return float(self.serial.read(self.serial.inWaiting()).decode().split('\r\n')[1])

    def close(self):
        self.serial.close()


if __name__ == '__main__':
    rate_table = RateTable()
    rate_table.en()
    rate_table.rate(10.0)
    print(rate_table.rate())
    rate_table.rate(0)
    print(rate_table.rate())
    rate_table.rate(-10.0)
    print(rate_table.rate())
    rate_table.rate(0)
    print(rate_table.rate())
    rate_table.dis()
    print(rate_table.rate())
    rate_table.close()
