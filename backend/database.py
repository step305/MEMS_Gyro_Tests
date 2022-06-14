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
            sql_req = 'CREATE TABLE IF NOT EXISTS sensors (name TEXT PRIMARY KEY);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            sql_req = 'CREATE TABLE IF NOT EXISTS bandwidth_result (id INTEGER PRIMARY KEY,' \
                      'name TEXT NOT NULL,' \
                      'date TIMESTAMP NOT NULL,' \
                      'bandwidth REAL NOT NULL,' \
                      'temperature REAL NOT NULL,' \
                      'data BLOB);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            sql_req = 'CREATE TABLE IF NOT EXISTS static_results (id INTEGER PRIMARY KEY,' \
                      'name TEXT NOT NULL,' \
                      'date TIMESTAMP NOT NULL,' \
                      'scale REAL NOT NULL,' \
                      'bias REAL NOT NULL,' \
                      'nonlin REAL NOT NULL,' \
                      'temperature REAL NOT NULL,' \
                      'data BLOB);'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            self.cursor.close()

        except sqlite3.Error as error:
            print('Error during connection to database:', error)

    def add_static_result(self, sensor, temperature):
        self.cursor = self.base_connection.cursor()
        sql_req = 'INSERT OR IGNORE INTO sensors (name) VALUES (?);'
        self.cursor.execute(sql_req, (sensor.name,))
        sql_req = 'INSERT INTO static_results (name, date, scale, bias, nonlin, data, temperature) ' \
                  'VALUES (?, ?, ?, ?, ?, ?, ?);'
        self.cursor.execute(sql_req, (sensor.name, datetime.datetime.now(),
                                      sensor.scale, sensor.bias, sensor.nonlin,
                                      pickle.dumps(sensor.history), temperature))
        self.base_connection.commit()
        self.cursor.close()

    def add_bandwidth_result(self, sensor, temperature):
        self.cursor = self.base_connection.cursor()
        sql_req = 'INSERT OR IGNORE INTO sensors (name) VALUES (?);'
        self.cursor.execute(sql_req, (sensor.name,))
        sql_req = 'INSERT INTO bandwidth_result (name, date, bandwidth, data, temperature) ' \
                  'VALUES (?, ?, ?, ?, ?);'
        self.cursor.execute(sql_req, (sensor.name, datetime.datetime.now(),
                                      sensor.bandwidth,
                                      pickle.dumps(sensor.out), temperature))
        self.base_connection.commit()
        self.cursor.close()

    def __del__(self):
        if self.base_connection:
            self.base_connection.close()


if __name__ == '__main__':
    pass
