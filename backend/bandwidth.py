import os
import matplotlib.pyplot as plt
import numpy as np
from drivers import PSU
import time
import datetime
import config
import multiprocessing as mp
from backend import database


def adc_process(sync_event, stop_event, result):
    import drivers.NIDAQ as NIDAQ
    import config

    print('ADC entry')
    adc = NIDAQ.NIDAQ(dev_id=config.NIDAQ_ID,
                      rate=config.ADC_RATE,
                      acq_time=config.ACQUISITION_TIME,
                      channels=config.ADC_CHANNELS)

    time.sleep(10)
    sync_event.set()
    print('ADC started')
    adc_data = adc.get()
    for sensor in config.Sensors:
        sensor.extract(adc_data)

    result.put(config.Sensors)
    stop_event.wait()
    print('ADC stopped')
    del adc


def rate_table_process(test_rate, sync_event, stop_event):
    import drivers.RateTable as RateTable

    print('Rate table entry')
    rate_table = RateTable.RateTable(port=config.RATE_TABLE_PORT, baud_rate=config.RATE_TABLE_BAUD_RATE)
    rate_table.en()
    rate_table.rate(0)
    print('Rate table wait')
    sync_event.wait(timeout=15.0)
    print('Rate table started')
    time.sleep(4.0)
    rate_table.rate(test_rate)
    stop_event.wait(timeout=15.0)
    print('Rate table stopped')
    rate_table.rate(0)
    rate_table.dis()
    del rate_table


def bandwidth_test(max_rate=100, result_path='result'):
    step_rate_event = mp.Event()
    step_rate_event.clear()
    ready_event = mp.Event()
    ready_event.clear()
    data = mp.Queue()

    result_full_path = os.path.abspath(result_path)
    if not os.path.isdir(result_full_path):
        os.mkdir(result_full_path)
    temp_results = os.path.join(result_full_path, 'temp_results')
    if not os.path.isdir(temp_results):
        os.mkdir(temp_results)

    print('Entry')
    psu = PSU.PSU(port=config.PSU_PORT,
                  baud_rate=config.PSU_BAUD_RATE,
                  voltages=config.PSU_CHANNEL_VOLT,
                  max_currents=config.PSU_CHANNEL_MAX_CURRENT)
    psu.on()
    time.sleep(10)
    print('Started')

    adc_proc = mp.Process(target=adc_process,
                          args=(step_rate_event, ready_event, data),
                          daemon=True)
    rate_table_proc = mp.Process(target=rate_table_process,
                                 args=(max_rate, step_rate_event, ready_event),
                                 daemon=True)
    rate_table_proc.start()
    adc_proc.start()

    sensor_data = data.get(timeout=100)

    ready_event.set()
    time.sleep(1)
    adc_proc.join()
    rate_table_proc.join()

    psu.off()
    del psu

    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    for sensor in sensor_data:
        ax.plot(sensor.out, sensor.plt_color_fmt)
        with open(os.path.join(temp_results, sensor.name + '.csv'), 'w') as f:
            for x in sensor.out:
                f.write('{:0.6}\r\n'.format(x))

    ax.legend([sensor.name for sensor in sensor_data])
    plt.grid()
    plt.show()
    fig.canvas.draw()
    fig.canvas.flush_events()
    fig.savefig(os.path.join(result_full_path, 'bandwidth.jpg'))
    plt.close(fig)

    for sensor in sensor_data:
        if sensor.name == '5V':
            continue
        w = np.abs(sensor.out)
        w0 = np.mean(w[config.ADC_RATE * 0.5:config.ADC_RATE * 2])
        we = np.mean(w[-config.ADC_RATE * 2:-config.ADC_RATE * 0.5])
        uL = w0 + (we - w0) * 0.2
        uH = w0 + (we - w0) * 0.8
        te = np.argwhere(np.abs(np.array(w[-config.ADC_RATE::-1])) < uH)
        if te.size > 0:
            te = int(te[0]) / config.ADC_RATE
        else:
            te = 9.8

        t0 = np.argwhere(np.abs(np.array(w[-config.ADC_RATE::-1])) < uL)
        if t0.size > 0:
            t0 = int(t0[0]) / config.ADC_RATE
        else:
            t0 = 0.1

        if te - t0 == 0:
            sensor.bandwidth = 500
        else:
            sensor.bandwidth = 1.0 / (te - t0)

    base = database.SensorsBase()
    for sensor in sensor_data:
        if sensor.name == '5V':
            continue
        base.add_bandwidth_result(sensor, 999)
    del base

    with open(os.path.join(result_full_path, 'bandwidth.txt'), 'w') as report:
        report.write('Bandwidth Test Results\r\n')
        report.write(str(datetime.datetime.now()) + '\r\n')
        report.write('-' * 80)
        report.write('\r\n')
        for sensor in sensor_data:
            if sensor.name == '5V':
                continue
            report.write(sensor.name + '\r\n')
            report.write('Bandwidth = {:0.3f}Hz\r\n'.format(sensor.bandwidth))
            report.write('*' * 40)
            report.write('\r\n')
            report.write('\r\n')


if __name__ == '__main__':
    pass
