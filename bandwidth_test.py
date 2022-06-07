from backend import bandwidth_test
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
    bandwidth_test.bandwidth_test(max_rate=config.rate_bandw,
                                  result_path=result_path)

    print('Press Enter to exit...')
    input()
