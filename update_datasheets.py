from backend import database


if __name__ == '__main__':
    d = database.SensorsBase()
    d.update_sensor_datasheets()
    del d
    print('Table "sensor_datasheet" updated!')
