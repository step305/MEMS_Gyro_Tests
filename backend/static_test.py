import os
import matplotlib.pyplot as plt
import numpy as np
import drivers.PSU as PSU
import drivers.NIDAQ as NIDAQ
import drivers.RateTable as RateTable
import time
import datetime
import config


def static_test(max_rate=100, step_rate=20, result_path='result'):
    rate_range = [r for r in range(-max_rate, max_rate + step_rate, step_rate)]
    result_full_path = os.path.abspath(result_path)
    if not os.path.isdir(result_full_path):
        os.mkdir(result_full_path)
    temp_results =os.path.join(result_full_path, 'temp_results')
    if not os.path.isdir(temp_results):
        os.mkdir(temp_results)

    psu = PSU.PSU(port=config.PSU_PORT,
                  baud_rate=config.PSU_BAUD_RATE,
                  voltages=config.PSU_CHANNEL_VOLT,
                  max_currents=config.PSU_CHANNEL_MAX_CURRENT)
    adc = NIDAQ.NIDAQ(dev_id=config.NIDAQ_ID,
                      rate=config.ADC_RATE,
                      acq_time=config.ACQUISITION_TIME,
                      channels=config.ADC_CHANNELS)
    rate_table = RateTable.RateTable(port=config.RATE_TABLE_PORT, baud_rate=config.RATE_TABLE_BAUD_RATE)
    rate_table.en()
    rate_table.rate(0)
    psu.on()
    time.sleep(5)

    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111)

    plots = []

    for sensor in config.Sensors:
        line, = ax.plot(0, 0, sensor.plt_color_fmt)
        plots.append(line)
    plt.xlim([-max(rate_range), max(rate_range)])
    ax.legend([sensor.name for sensor in config.Sensors])
    plt.ylim([-10, 10])
    plt.grid()
    plt.show()
    fig.canvas.draw()
    fig.canvas.flush_events()

    for rate in rate_range:
        rate_table.rate(rate)
        time.sleep(3)
        adc_data = adc.get()
        means = ''
        for sensor, line in zip(config.Sensors, plots):
            sensor.extract(adc_data)
            sensor.add(rate, sensor.mean_value, sensor.std_value)
            means += '{:0.3f}V\t'.format(sensor.mean_value)
            line.set_ydata([k[1] for k in sensor.history])
            line.set_xdata([k[0] for k in sensor.history])
            fig.canvas.draw()
            fig.canvas.flush_events()
        print('test rate = {:0.2f}dps\tOut: '.format(rate) + means)
    rate_table.rate(0)
    rate_table.dis()
    del rate_table
    plt.close()

    for sensor in config.Sensors:
        if sensor.name == '5V':
            continue
        x = [k[0] for k in sensor.history]
        y = [k[1] for k in sensor.history]
        noise = [k[2] for k in sensor.history]

        p = np.polyfit(x, y, 1)
        sensor.scale = p[0]
        sensor.bias = p[1]
        dx = [iy - (p[0] * ix + p[1]) for ix, iy in zip(x, y)]
        dx = [dxi / np.abs(p[0]) / max(rate_range) * 100.0 for dxi in dx]
        sensor.nonlin = np.max(np.abs(dx))
        with open(os.path.join(temp_results, sensor.name + '.csv'), 'w') as f:
            f.write('Rate;Out,V;Nonlinearity, %;STD out, V\r\n')
            for xi, yi, wi, dxi in zip(x, y, noise, dx):
                f.write('{:0.2f};{:0.6f};{:0.6f};{:0.6f}\r\n'.format(xi, yi, dxi, wi))

    with open(os.path.join(result_full_path, 'static_result.txt'), 'w') as report:
        report.write('Static Test Results\r\n')
        report.write(str(datetime.datetime.now()) + '\r\n')
        report.write('-' * 80)
        report.write('\r\n')
        for sensor in config.Sensors:
            if sensor.name == '5V':
                continue
            report.write(sensor.name + '\r\n')
            report.write('Scale Factor = {:0.3f}mV/dps\r\n'.format(sensor.scale * 1000.0))
            report.write('Bias = {:0.3f}dps\r\n'.format(sensor.bias / sensor.scale))
            report.write('Nonlinearity = {:0.3f}%\r\n'.format(sensor.nonlin))
            report.write('Noise = {:0.3f}dps\r\n'.format(sensor.history[
                                                      int(len(rate_range)/2 + 0.5)
                                                  ][2] / sensor.scale))
            report.write('*' * 40)
            report.write('\r\n')
            report.write('\r\n')

    psu.off()
    del psu
    del adc
