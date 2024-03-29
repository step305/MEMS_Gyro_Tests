import datetime
import sqlite3
import pickle
import config


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

            # create (if not exists) table for storing test runs ID
            sql_req = 'CREATE TABLE IF NOT EXISTS tests (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT DEFAULT 0,' \
                      'test_count INTEGER NOT NULL UNIQUE);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()

            # create (if not exists) table for storing tested sensors info
            sql_req = 'CREATE TABLE IF NOT EXISTS sensors (id INTEGER PRIMARY KEY , name TEXT NOT NULL, ' \
                      'sensor_id TEXT, UNIQUE (name, sensor_id) ON CONFLICT IGNORE);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()

            # create (if not exists) table for storing bandwidth test results
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

            # create (if not exists) table for storing static test results
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

            # create (if not exists) table for storing thermal test results
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

            # create (if not exists) table for storing short-therm stability test (Allan diagram params) results
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
            self.cursor.execute(sql_req)
            self.base_connection.commit()

            # create (if not exists) table for storing most recent (actual) results for each sensor
            sql_req = 'CREATE TABLE IF NOT EXISTS sensor_datasheet (id INTEGER PRIMARY KEY,' \
                      'name TEXT NOT NULL,' \
                      'sensor_id TEXT DEFAULT "",' \
                      'date TIMESTAMP NOT NULL DEFAULT 0,' \
                      'scale REAL DEFAULT 0,' \
                      'bias REAL DEFAULT 0,' \
                      'nonlin REAL DEFAULT 0,' \
                      'max_scale_in_temperature REAL DEFAULT 0,' \
                      'max_bias_in_temperature REAL DEFAULT 0,' \
                      'arw REAL DEFAULT 0,' \
                      'bias_instability REAL DEFAULT 0,' \
                      'static_results_id INTEGER DEFAULT 0,' \
                      'thermal_results_id INTEGER DEFAULT 0,' \
                      'stability_results_id INTEGER DEFAULT 0,' \
                      'comment TEXT DEFAULT "", UNIQUE (name, sensor_id) ON CONFLICT REPLACE);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()

            self.cursor.close()

        except sqlite3.Error as error:
            print('Error during connection to database: ', error)

    def add_static_result(self, test_id, test_type, sensor, temperature, rate_max, thermal_test_flag=False):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'INSERT OR IGNORE INTO sensors (name, sensor_id) VALUES (?,?);'
            self.cursor.execute(sql_req, (sensor.name, sensor.id))
            if not thermal_test_flag:
                sql_req = 'INSERT INTO static_results (name, sensor_id, test_id, test_type, date, scale, ' \
                          'bias, nonlin, rate_max, data, temperature, test_type, comment) ' \
                          'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
                self.cursor.execute(sql_req, (sensor.name, sensor.id, test_id, test_type, datetime.datetime.now(),
                                              sensor.scale, sensor.bias, sensor.nonlin, rate_max,
                                              pickle.dumps(sensor.history), temperature,
                                              sensor.test_type, sensor.comment))
            else:
                sql_req = 'INSERT INTO thermal_results (name, sensor_id, test_id, test_type, date, scale, ' \
                          'bias, nonlin, rate_max, data, temperature, test_type, comment) ' \
                          'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
                self.cursor.execute(sql_req, (sensor.name, sensor.id, test_id, test_type, datetime.datetime.now(),
                                              sensor.scale, sensor.bias, sensor.nonlin, rate_max,
                                              pickle.dumps(sensor.history), temperature,
                                              sensor.test_type, sensor.comment))
            self.base_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print('Error during storing static test results to database: ', error)

    def add_bandwidth_result(self, test_id, test_type, sensor, temperature, rate):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'INSERT OR IGNORE INTO sensors (name, sensor_id) VALUES (?, ?);'
            self.cursor.execute(sql_req, (sensor.name, sensor.id))
            sql_req = 'INSERT INTO bandwidth_result (name, sensor_id, test_id, date, ' \
                      'bandwidth, rate_max, data, temperature, test_type, comment) ' \
                      'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
            self.cursor.execute(sql_req, (sensor.name, sensor.id, test_id, datetime.datetime.now(),
                                          sensor.bandwidth, rate,
                                          pickle.dumps(sensor.out), temperature,
                                          test_type, sensor.comment))
            self.base_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print('Error during storing bandwidth test results to database: ', error)

    def add_stability_result(self, test_id, test_type, sensor, temperature):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'INSERT INTO stability_results (name, sensor_id, test_id, date, ' \
                      'arw, bias_instabiluty, temperature, test_type, comment, data) ' \
                      'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
            self.cursor.execute(sql_req, (sensor.name, sensor.id, test_id, datetime.datetime.now(),
                                          sensor.arw, sensor.bias_instability,
                                          temperature, test_type, sensor.comment,
                                          pickle.dumps([sensor.long_therm_out, sensor.tau, sensor.adev])))
            self.base_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print('Error during storing stability test results to database: ', error)

    def start_new_test(self):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT ifnull(MAX(test_count) ,0) FROM tests;'
            self.cursor.execute(sql_req)
            sql_req = 'INSERT INTO tests (test_count) VALUES ((SELECT ifnull(MAX(test_count) ,0) FROM tests) + 1);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            print('Error during storing new test ID to database: ', error)

    def get_last_test_id(self):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT ifnull(MAX(test_count) ,0) FROM tests;'
            self.cursor.execute(sql_req)
            test_id, = self.cursor.fetchone()
            self.base_connection.commit()
            self.cursor.close()
            return test_id
        except sqlite3.Error as error:
            print('Error during storing new test ID to database: ', error)

    def get_sensor_params(self, sensor_name, sensor_id):
        try:
            sensor = config.RateSensor(name=sensor_name, sensor_id=sensor_id)
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT scale, bias, nonlin FROM sensor_datasheet WHERE name=? AND sensor_id=?;'
            self.cursor.execute(sql_req, (sensor_name, sensor_id))
            params = self.cursor.fetchone()
            scale, bias, nonlin = params
            sensor.scale = scale
            sensor.bias = bias
            sensor.nonlin = nonlin
            sql_req = 'SELECT bandwidth, MAX(date) ' \
                      'FROM bandwidth_result WHERE name = ? AND sensor_id = ?;'
            self.cursor.execute(sql_req, (sensor_name, sensor_id))
            params = self.cursor.fetchone()
            bandwidth, _ = params
            sensor.bandwidth = bandwidth
            return sensor
        except sqlite3.Error as error:
            print('Error during fetching sensor parameters from datasheet', sensor_name, sensor_id, error)

    def get_sensor_static_graph(self, sensor):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT data, MAX(date) FROM static_results WHERE name=? AND sensor_id=?;'
            self.cursor.execute(sql_req, (sensor.name, sensor.id))
            params = self.cursor.fetchone()
            data_pickled, _ = params
            data = pickle.loads(data_pickled)
            sensor.history = data
            return sensor
        except sqlite3.Error as error:
            print('Error during fetching sensor static graph', sensor.name, sensor.id, error)

    def list_all_sensors(self):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT name, sensor_id from sensors;'
            self.cursor.execute(sql_req)
            result = self.cursor.fetchall()
            sensors_names = [d[0] for d in result]
            sensors_ids = [d[1] for d in result]
            self.base_connection.commit()
            self.cursor.close()
            return sensors_names, sensors_ids

        except sqlite3.Error as error:
            print('Error during updating sensors datasheet in database: ', error)

    def update_sensor_datasheets(self):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT name, sensor_id from sensors;'
            self.cursor.execute(sql_req)
            result = self.cursor.fetchall()
            print(result)
            for result_i in result:
                name, sensor_id = result_i
                if name == '5V':
                    continue
                sql_req = 'SELECT id, name, scale, bias, nonlin, MAX(date) ' \
                          'FROM static_results WHERE name = ? AND sensor_id = ?;'
                self.cursor.execute(sql_req, (name, sensor_id))
                params = self.cursor.fetchone()
                result_id, sensor_name, scale, bias, nonlin, params_date = params
                print(params)
                sql_req = 'INSERT OR IGNORE INTO sensor_datasheet (name, sensor_id) VALUES (?, ?);'
                self.cursor.execute(sql_req, (name, sensor_id))
                self.base_connection.commit()
                sql_req = 'UPDATE sensor_datasheet SET scale = ?,' \
                          'bias = ?,' \
                          'date = ?,' \
                          'nonlin = ? ' \
                          'WHERE sensor_id = ? AND name = ?;'
                self.cursor.execute(sql_req, (scale, bias, params_date, nonlin, sensor_id, name))
            self.base_connection.commit()
            self.cursor.close()

        except sqlite3.Error as error:
            print('Error during updating sensors datasheet in database: ', error)

    def close(self):
        if self.base_connection:
            self.base_connection.close()


if __name__ == '__main__':
    pass
