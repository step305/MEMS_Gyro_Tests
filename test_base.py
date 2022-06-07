from backend import database
import os
import config


if __name__ == '__main__':
    test = database.SensorsBase(path_to_base=os.path.abspath(os.path.join(os.path.curdir, 'database', 'database.db')))
    for s in config.Sensors:
        if s.name == '5V':
            continue
        test.add_static_result(s, 999)
    del test
