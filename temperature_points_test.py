from backend import temperature_points
import config
import datetime
import os


if __name__ == '__main__':
    temperature_points.temperature_points_test(temperature_points=config.TEMPERATURE_POINTS)
    print('Press Enter to exit...')
    input()
