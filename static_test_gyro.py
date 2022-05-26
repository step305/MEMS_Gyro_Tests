import time
import matplotlib.pyplot as plt
import numpy as np
import datetime
import drivers.PSU as PSU
import drivers.NIDAQ as NIDAQ
import drivers.RateTable as RateTable
import config


if __name__ == '__main__':
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

    for col in config.SENSORS_COLOR:
        line, = ax.plot(0, 0, col)
        plots.append(line)
    plt.xlim([-config.MAX_RATE, config.MAX_RATE])
    ax.legend([sensor.name for sensor in config.Sensors])
    plt.ylim([-12, 12])
    plt.show()
    fig.canvas.draw()
    fig.canvas.flush_events()

    for rate in config.TEST_RATES:
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

    for sensor in config.Sensors:
        if sensor.name == '5V':
            continue
        x = [k[0] for k in sensor.history]
        y = [k[1] for k in sensor.history]
        p = np.polyfit(x, y, 1)
        sensor.scale = p[0]
        sensor.bias = p[1]
        dx = [iy - (p[0] * ix + p[1]) for ix, iy in zip(x, y)]
        sensor.nonlin = np.max(np.abs(dx)) / np.abs(p[0]) / config.MAX_RATE * 100.0

    with open('static_result.txt', 'w') as report:
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
                                                      int(len(config.TEST_RATES)/2 + 0.5)
                                                  ][2] / sensor.scale))
            report.write('*' * 40)
            report.write('\r\n')
            report.write('\r\n')

    psu.off()
    del psu
    del adc

    print('Press Enter to exit...')
    input()


