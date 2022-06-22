import os
import matplotlib.pyplot as plt
import numpy as np
from drivers import PSU
from drivers import NIDAQ
import time
import datetime
import config
from backend import database
import allantools
import scipy.io


def stability_test(test_id, duration=200, result_path='result', temperature=999):
    result_full_path = os.path.abspath(result_path)
    if not os.path.isdir(result_full_path):
        os.mkdir(result_full_path)

    for sensor in config.Sensors:
        sensor.reset_results()

    db = database.SensorsBase()
    for sensor in config.Sensors:
        temp_sensor = db.get_sensor_params(sensor.name, sensor.id)
        sensor.scale = temp_sensor.scale
        sensor.bias = sensor.bias
        sensor.nonlin = sensor.nonlin

    del db

    psu = PSU.PSU(port=config.PSU_PORT,
                  baud_rate=config.PSU_BAUD_RATE,
                  voltages=config.PSU_CHANNEL_VOLT,
                  max_currents=config.PSU_CHANNEL_MAX_CURRENT)
    adc = NIDAQ.NIDAQ(dev_id=config.NIDAQ_ID,
                      rate=config.ADC_RATE,
                      acq_time=config.ACQUISITION_TIME,
                      channels=config.ADC_CHANNELS)

    psu.on()
    time.sleep(25)

    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    plots = []

    for sensor in config.Sensors:
        line, = ax.plot(0, 0, sensor.plt_color_fmt)
        plots.append(line)

    ax.legend([sensor.name for sensor in config.Sensors])
    plt.grid()
    plt.show()
    fig.canvas.draw()
    fig.canvas.flush_events()

    dT = config.ACQUISITION_TIME

    for t in range(0, dT, duration):
        adc_data = adc.get()
        means = ''
        for sensor, line in zip(config.Sensors, plots):
            sensor.extract(adc_data)
            sensor.add(sensor.mean_value, sensor.std_value)
            sensor.add_long_therm(sensor.out)

            means += '{:0.3f}V\t'.format(sensor.mean_value)
            line.set_ydata([k[1] for k in sensor.history])
            line.set_xdata([k[0] for k in sensor.history])
            fig.canvas.draw()
            fig.canvas.flush_events()

    plt.close()

    for sensor in config.Sensors:
        if sensor.name == '5V':
            continue

        data = np.array(sensor.long_therm_out)
        data = data / (sensor.scale / 1000.0) - sensor.bias
        data = data * 3600
        data = data.tolist()

        (tau, adev, adev_error, adev_amount) = allantools.oadev(data, rate=config.ADC_RATE,
                                                                data_type='phase', taus='decade')
        matlab_result = {
            'tau': np.array(tau),
            'adev': np.array(adev),
            'data': data,
            'freq': config.ADC_RATE
        }

        scipy.io.savemat(os.path.join(result_full_path, '{}-{}.mat'.format(sensor.name, sensor.id)),
                         mdict=matlab_result,
                         appendmat=False,
                         format='5',
                         long_field_names=False,
                         do_compression=False,
                         oned_as='column')

        adev = np.array(adev)
        tau = np.array(tau)
        sensor.adev = adev
        sensor.tau = tau

        logadev = np.log10(adev)
        logtau = np.log10(tau / 3600.0)

        slope = -0.5
        dlogadev = np.diff(logadev) / np.diff(logtau)

        i = np.argmin(np.abs(dlogadev - slope))
        b = logadev[i] - slope * logtau[i]
        logN = slope * np.log(1) + b
        ARW = 10**logN
        sensor.arw = ARW

        bias_instability = np.min(adev) / 2 / np.log(2) * np.pi
        sensor.bias_instability = bias_instability

    db = database.SensorsBase()
    for sensor in config.Sensors:
        if sensor.name == '5V':
            continue
        db.add_stability_result(test_id, config.TEST_TYPE, sensor, temperature)
    del db

    with open(os.path.join(result_full_path, 'stability_result.txt'), 'w') as report:
        report.write('Stability Test Results\r\n')
        report.write(str(datetime.datetime.now()) + '\r\n')
        report.write('-' * 80)
        report.write('\r\n')
        for sensor in config.Sensors:
            if sensor.name == '5V':
                continue
            report.write(sensor.name + ': ' + sensor.id + '\r\n')
            report.write('ARW = {:0.3f}deg/sqrt(h)\r\n'.format(sensor.arw))
            report.write('Bias instability = {:0.3f}dph\r\n'.format(sensor.bias_instability))
            report.write('*' * 40)
            report.write('\r\n')
            report.write('\r\n')

    psu.off()
    del psu
    del adc


