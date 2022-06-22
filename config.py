import numpy as np
import os

SENSORS_DATABASE = os.path.abspath(os.path.join(os.path.curdir, 'database', 'database.db'))
TEST_TYPES = (
    'первичный',
    'после вибрации',
    'после удара',
    'после перегрузки',
    'после термоцикла',
    'финальный'
)
TEST_TYPE = TEST_TYPES[0]


class RateSensor:
    def __init__(self,
                 name='',
                 sensor_id='',
                 out=None,
                 ref=None,
                 temper=None,
                 comment='',
                 plt_color='b-.'):
        self.out_chan = out
        self.temp_chan = temper
        self.ref_chan = ref
        self.mean_value = 0.0
        self.std_value = 0.0
        self.temper_value = 0.0
        self.history = []
        self.scale = 0
        self.bias = 0
        self.nonlin = 0
        self.name = name
        self.id = sensor_id
        self.plt_color_fmt = plt_color
        self.out = []
        self.bandwidth = 0
        self.test_type = TEST_TYPE
        self.comment = comment
        self.long_therm_out = []
        self.arw = 0
        self.bias_instability = 0
        self.adev = []
        self.tau = []

    def add_long_therm(self, data):
        self.long_therm_out.extend(data)

    def extract(self, adc_result):
        self.out = adc_result[self.out_chan]
        if self.ref_chan or self.ref_chan == 0:
            self.out = [o - r for o, r in zip(self.out, adc_result[self.ref_chan])]
        self.mean_value = np.mean(self.out)
        self.std_value = np.std(self.out)
        if self.temper_value:
            self.temper_value = np.mean(adc_result[self.temp_chan])

    def add(self, rate, out, stdout):
        self.history.append((rate, out, stdout))

    def reset_results(self):
        self.history = []
        self.mean_value = 0
        self.std_value = 0
        self.temper_value = 0
        self.bandwidth = 0
        self.scale = 0
        self.bias = 9
        self.nonlin = 0
        self.out = []
        self.long_therm_out = []

    def __str__(self):
        return 'Sensor {}, serial num {}: scale={:.3f}mV/dps, bias={:.3f}dps, nonlin={:.2f}%'.format(self.name,
                                                                                                     self.id,
                                                                                                     self.scale,
                                                                                                     self.bias,
                                                                                                     self.nonlin)

# PSU configuration
PSU_PORT = 'COM28'
PSU_BAUD_RATE = 9600
PSU_CHANNEL_VOLT = [12.0, 12.0, 5.0]
PSU_CHANNEL_MAX_CURRENT = [1.0, 1.0, 1.2]

# rate table configuration
RATE_TABLE_PORT = 'COM7'
RATE_TABLE_BAUD_RATE = 38400

# Thermo (climatic) camera configuration
THERMO_PORT = 'COM15'
THERMO_BAUDRATE = 19200

# NIDAQ configuration
ADC_CHANNELS = [0, 8, 1, 9, 3, 11, 5, 4, 12, 13, 6, 14, 7, 15, 16, 24, 18, 17, 25, 26, 20]
NIDAQ_ID = 'Dev5'
ADC_RATE = 1000
ACQUISITION_TIME = 10
Sensors = [
    RateSensor(name='VG910', sensor_id='1', out=0, temper=1, comment='Fizoptika', plt_color='b-.'),
    RateSensor(name='VG910', sensor_id='2', out=2, temper=3, comment='Fizoptika', plt_color='r-.'),
    RateSensor(name='TG100', sensor_id='1', out=4, ref=5, temper=6, comment='MPLab', plt_color='g-.'),
    RateSensor(name='TG100', sensor_id='2', out=7, ref=8, temper=9, comment='MPLab', plt_color='y-.'),
    RateSensor(name='CRH02', sensor_id='0', out=10, ref=11, temper=12, comment='SiliconSensing', plt_color='b*'),
    RateSensor(name='CRS03', sensor_id='0', out=13, comment='SiliconSensing', plt_color='k*'),
    RateSensor(name='TG19A', sensor_id='0', out=14, ref=15, temper=16, comment='SiliconSensing', plt_color='m*'),
    RateSensor(name='CRS09', sensor_id='0', out=17, ref=18, temper=19, comment='MPLab', plt_color='c*'),
    RateSensor(name='5V', sensor_id='-1', out=20, comment='power rail', plt_color='g*')
]

# static test plan
MAX_RATE = [100, 75]
RATE_STEP = [20, 15]

# bandwidth test plan
rate_bandw = 50

# temperature points test plan
TEMPERATURE_POINTS = [-50, -40, -20, 0, 20, 40, 60, 85]
TEMPERATURE_POINT_TOLERANCE = 0.3
TIME_HOLD_ON_TEMPERATURE = 30  # minutes

# stability test plan
DURATION = 3600
