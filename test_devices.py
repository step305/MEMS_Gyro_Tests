import nidaqmx
from nidaqmx import constants
import numpy as np
import time
import serial

FC = 1000
SAMPLES_PER_CHANNEL = 1000
NIDAQ_ID = 'Dev5'
PSU_PORT = 'COM28'
RATE_TABLE_PORT = 'COM7'


if __name__ == '__main__':
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(NIDAQ_ID + "/ai0")
        task.ai_channels.add_ai_voltage_chan(NIDAQ_ID + "/ai1")
        task.ai_channels.add_ai_voltage_chan(NIDAQ_ID + "/ai5")
        task.timing.cfg_samp_clk_timing(rate=FC, sample_mode=constants.AcquisitionType.FINITE,
                                        samps_per_chan=SAMPLES_PER_CHANNEL)

        t_start = time.time()
        data = task.read(number_of_samples_per_channel=SAMPLES_PER_CHANNEL, timeout=20)
        t_end = time.time()
        print('Ni-DAQMX test')
        print(len(data), len(data[0]), t_end - t_start)
        print(np.mean(data), np.mean(data[1]))

        psu_port = serial.Serial(port=PSU_PORT, baudrate=9600, timeout=0.2)
        if psu_port.inWaiting() > 0:
            psu_port.read(psu_port.inWaiting())
        psu_port.write(':CHAN2:VOLT 4.51\n'.encode())
        time.sleep(0.2)
        if psu_port.inWaiting() > 0:
            psu_port.read(psu_port.inWaiting())
        psu_port.write(':CHAN2:VOLT?\n'.encode())
        time.sleep(0.2)
        psu_answer = float(psu_port.read(psu_port.inWaiting()).decode())
        psu_port.close()
        print('PSU test')
        print(psu_answer)

        rate_table_port = serial.Serial(port=RATE_TABLE_PORT, baudrate=38400, timeout=5)
        rate_table_port.write('OPMODE 0\r\n'.encode())
        time.sleep(0.2)
        rate_table_port.write('EN\r\n'.encode())
        time.sleep(0.2)

        rate_table_port.write('J 30\r\n'.encode())
        time.sleep(0.5)

        if rate_table_port.inWaiting() > 0:
            rate_table_port.read(rate_table_port.inWaiting())
        rate_table_port.write('J\r\n'.encode())
        time.sleep(0.2)
        rate_table_answer = float(rate_table_port.read(rate_table_port.inWaiting()).decode().split('\r\n')[1])
        print(rate_table_answer)

        rate_table_port.write('J 0\r\n'.encode())
        time.sleep(0.2)

        if rate_table_port.inWaiting() > 0:
            rate_table_port.read(rate_table_port.inWaiting())
        rate_table_port.write('J\r\n'.encode())
        time.sleep(0.2)
        rate_table_answer = float(rate_table_port.read(rate_table_port.inWaiting()).decode().split('\r\n')[1])
        print(rate_table_answer)

        rate_table_port.write('DIS\r\n'.encode())
        time.sleep(0.2)
        rate_table_port.close()

        print('Rate Table test')

        print('Press Enter to exit...')
        input()
