from drivers import ThermalChamber
from backend import static_test
import config
import os
import time
import datetime

TIME_HOLD_ON_TEMPERATURE = 30  # minutes


def temperature_points_test(test_id, temperature_points=(-40, 0, 20, 85)):
    temperature_chamber = ThermalChamber.ThermalChamber(port=config.THERMO_PORT, baud_rate=config.THERMO_BAUDRATE)
    now_date = datetime.datetime.now()
    result_path = os.path.join(os.path.abspath(os.path.curdir), 'results')
    if not os.path.isdir(result_path):
        os.mkdir(result_path)
    result_path = os.path.join(result_path, '{}-{}-{} {}_{}'.format(now_date.day,
                                                                    now_date.month,
                                                                    now_date.year,
                                                                    now_date.hour,
                                                                    now_date.minute))
    if not os.path.isdir(result_path):
        os.mkdir(result_path)
    result_path = os.path.join(result_path, 'temperature')
    if not os.path.isdir(result_path):
        os.mkdir(result_path)

    for temperature_point in temperature_points:
        temperature_chamber.set_temperature(temperature_point)
        act_temperature = temperature_chamber.get_temperature()
        print()
        print('Setting next temperature point = {:.1f}'.format(temperature_point))
        while abs(act_temperature - temperature_point) > config.TEMPERATURE_POINT_TOLERANCE:
            time.sleep(60)
            act_temperature = temperature_chamber.get_temperature()
            print(datetime.datetime.now(), 'Target temperature = {:0.1f} '
                  'Actual temperature = {:.1f}'.format(temperature_point, act_temperature))

        print()
        print('Hold on temperature point = {:0.1f}'.format(temperature_point))
        t0 = time.time()
        while (time.time() - t0) < config.TIME_HOLD_ON_TEMPERATURE * 60:
            time.sleep(60)
            act_temperature = temperature_chamber.get_temperature()
            print(datetime.datetime.now(), 'Target temperature = {:0.1f} '
                  'Actual temperature = {:.1f} '
                  'Hold {:.1f} of {:.1f} minutes'.format(temperature_point,
                                                         act_temperature,
                                                         (time.time() - t0) / 60.0,
                                                         config.TIME_HOLD_ON_TEMPERATURE))

        result_point_path = os.path.join(result_path, '{:.1f}'.format(temperature_point))
        if not os.path.isdir(result_point_path):
            os.mkdir(result_point_path)

        print()
        print('Starting static test...')

        for max_rate, rate_step in zip(config.MAX_RATE, config.RATE_STEP):
            static_test.static_test(test_id,
                                    max_rate=max_rate,
                                    step_rate=rate_step,
                                    result_path=os.path.join(result_point_path, '{:0.1f}'.format(max_rate)),
                                    temperature=temperature_point)

        print('Static test done!')

    temperature_chamber.set_temperature(27)
    act_temperature = temperature_chamber.get_temperature()
    print()
    print('Going to normal conditions')
    while abs(act_temperature - 27) > config.TEMPERATURE_POINT_TOLERANCE:
        time.sleep(60)
        act_temperature = temperature_chamber.get_temperature()
        print(datetime.datetime.now(), 'Target temperature = {:0.1f} '
                                       'Actual temperature = {:.1f}'.format(27, act_temperature))

    temperature_chamber.off()
    print()
    print('Temperature test done!')

