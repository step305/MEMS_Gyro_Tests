from backend import bandwidth
from backend import database
import config
import datetime
import os

if __name__ == '__main__':
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
    result_path = os.path.join(result_path, 'bandwidth')
    if not os.path.isdir(result_path):
        os.mkdir(result_path)
    print('Go')
    d = database.SensorsBase()
    d.start_new_test()
    test_id = d.get_last_test_id()
    del d
    bandwidth.bandwidth_test(test_id,
                             max_rate=config.rate_bandw,
                             result_path=result_path)

    print('Press Enter to exit...')
    input()
