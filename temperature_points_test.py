from backend import temperature_points
from backend import database
import config
import datetime
import os


if __name__ == '__main__':
    d = database.SensorsBase()
    d.start_new_test()
    test_id = d.get_last_test_id()
    del d
    temperature_points.temperature_points_test(test_id, temperature_points=config.TEMPERATURE_POINTS)
    print('Press Enter to exit...')
    input()
