from backend import stability
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
    result_path = os.path.join(result_path, 'stability')
    if not os.path.isdir(result_path):
        os.mkdir(result_path)

    d = database.SensorsBase()
    d.start_new_test()
    test_id = d.get_last_test_id()
    del d

    stability.stability_test(test_id, config.DURATION,
                             result_path, 999)

    print('Press Enter to exit...')
    input()
