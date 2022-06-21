import datetime
import pickle
import sqlite3


class SensorsBase:
    def __init__(self, path_to_base='database\\database.db'):
        try:
            print('connecting')
            self.base_connection = sqlite3.connect(path_to_base)
            print('connected')
            self.cursor = self.base_connection.cursor()
            sql_req = 'select sqlite_version();'
            self.cursor.execute(sql_req)
            record = self.cursor.fetchall()
            print(record)
            sql_req = 'CREATE TABLE IF NOT EXISTS tests (id INTEGER PRIMARY KEY DEFAULT 0);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            sql_req = 'CREATE TABLE IF NOT EXISTS sensors (name TEXT PRIMARY KEY);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            sql_req = 'CREATE TABLE IF NOT EXISTS bandwidth_result (id INTEGER PRIMARY KEY,' \
                      'name TEXT NOT NULL, ' \
                      'sensor_id TEXT, ' \
                      'test_id INTEGER NOT NULL,' \
                      'date TIMESTAMP NOT NULL,' \
                      'bandwidth REAL NOT NULL,' \
                      'temperature REAL NOT NULL,' \
                      'rate_max REAL NOT NULL,' \
                      'test_type TEXT,' \
                      'comment TEXT,' \
                      'data BLOB);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            sql_req = 'CREATE TABLE IF NOT EXISTS static_results (id INTEGER PRIMARY KEY,' \
                      'name TEXT NOT NULL,' \
                      'sensor_id TEXT,' \
                      'test_id INTEGER NOT NULL,' \
                      'date TIMESTAMP NOT NULL,' \
                      'scale REAL NOT NULL,' \
                      'bias REAL NOT NULL,' \
                      'nonlin REAL NOT NULL,' \
                      'temperature REAL NOT NULL,' \
                      'rate_max REAL NOT NULL,' \
                      'test_type TEXT,' \
                      'comment TEXT,' \
                      'data BLOB);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            sql_req = 'CREATE TABLE IF NOT EXISTS thermal_results (id INTEGER PRIMARY KEY,' \
                      'name TEXT NOT NULL,' \
                      'sensor_id TEXT,' \
                      'test_id INTEGER NOT NULL,' \
                      'date TIMESTAMP NOT NULL,' \
                      'scale REAL NOT NULL,' \
                      'bias REAL NOT NULL,' \
                      'nonlin REAL NOT NULL,' \
                      'temperature REAL NOT NULL,' \
                      'rate_max REAL NOT NULL,' \
                      'test_type TEXT,' \
                      'comment TEXT,' \
                      'data BLOB);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            sql_req = 'CREATE TABLE IF NOT EXISTS stability_results (id INTEGER PRIMARY KEY,' \
                      'name TEXT NOT NULL,' \
                      'sensor_id TEXT,' \
                      'test_id INTEGER NOT NULL,' \
                      'date TIMESTAMP NOT NULL,' \
                      'arw REAL NOT NULL,' \
                      'bias_instabiluty REAL NOT NULL,' \
                      'temperature REAL NOT NULL,' \
                      'test_type TEXT,' \
                      'comment TEXT,' \
                      'data BLOB);'
            sql_req = 'CREATE TABLE IF NOT EXISTS sensor_datasheet (id INTEGER PRIMARY KEY,' \
                      'name TEXT NOT NULL,' \
                      'sensor_id TEXT,' \
                      'date TIMESTAMP NOT NULL,' \
                      'scale REAL,' \
                      'bias REAL,' \
                      'nonlin REAL,' \
                      'max_scale_in_temperature REAL,' \
                      'max_bias_in_temperature REAL' \
                      'arw REAL,' \
                      'bias_instability REAL,' \
                      'static_results_id INTEGER,' \
                      'thermal_results_id INTEGER,' \
                      'stability_results_id INTEGER,' \
                      'comment TEXT);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            self.cursor.close()

        except sqlite3.Error as error:
            print('Error during connection to database:', error)

    def add_static_result(self, test_id, sensor, temperature, rate_max):
        self.cursor = self.base_connection.cursor()
        sql_req = 'INSERT OR IGNORE INTO sensors (name) VALUES (?);'
        self.cursor.execute(sql_req, (sensor.name,))
        sql_req = 'INSERT INTO static_results (name, sensor_id, test_id, date, scale, ' \
                  'bias, nonlin, rate_max, data, temperature, test_type, comment) ' \
                  'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
        self.cursor.execute(sql_req, (sensor.name, sensor.id, test_id, datetime.datetime.now(),
                                      sensor.scale, sensor.bias, sensor.nonlin, rate_max,
                                      pickle.dumps(sensor.history), temperature,
                                      sensor.test_type, sensor.comment))
        self.base_connection.commit()
        self.cursor.close()

    def add_bandwidth_result(self, test_id, sensor, temperature, rate):
        self.cursor = self.base_connection.cursor()
        sql_req = 'INSERT OR IGNORE INTO sensors (name) VALUES (?);'
        self.cursor.execute(sql_req, (sensor.name,))
        sql_req = 'INSERT INTO bandwidth_result (name, test_id, date, ' \
                  'bandwidth, rate_max, data, temperature, test_type, comment) ' \
                  'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);'
        self.cursor.execute(sql_req, (sensor.name, test_id, datetime.datetime.now(),
                                      sensor.bandwidth, rate,
                                      pickle.dumps(sensor.out), temperature,
                                      sensor.test_type, sensor.comment))
        self.base_connection.commit()
        self.cursor.close()

    def __del__(self):
        if self.base_connection:
            self.base_connection.close()


if __name__ == '__main__':
    pass
