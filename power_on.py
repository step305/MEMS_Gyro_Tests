from drivers import PSU
import config

if __name__ == '__main__':
    psu = PSU.PSU(port=config.PSU_PORT,
                  baud_rate=config.PSU_BAUD_RATE,
                  voltages=config.PSU_CHANNEL_VOLT,
                  max_currents=config.PSU_CHANNEL_MAX_CURRENT)
    psu.on()
    print('Press Enter to stop')
    input()
    del psu
