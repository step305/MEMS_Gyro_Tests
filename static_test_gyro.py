from backend import static_test
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
    result_path = os.path.join(result_path, 'static')
    if not os.path.isdir(result_path):
        os.mkdir(result_path)
    for max_rate, rate_step in zip(config.MAX_RATE, config.RATE_STEP):
        static_test.static_test(max_rate=max_rate,
                                step_rate=rate_step,
                                result_path=os.path.join(result_path, '{:0.1f}'.format(max_rate)))

    print('Press Enter to exit...')
    input()
