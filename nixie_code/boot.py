# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
from wifinet import *
from machine import Pin, RTC
import time
from nixie_lamps import NixieLamp

lamp_nix = NixieLamp() # prepare Nixie class

with open('boot.ini', 'r') as input:
    settings = json.load(input)

for i in range(4):
    buttonPin = Pin(13, Pin.IN, Pin.PULL_DOWN) # check button for REST
    lamp_nix.display_number(f'000{i}') # in string
    time.sleep(0.5)
    
    if buttonPin.value() == 1:
        print('Reset detected')
        print("Reset to station mode")
        settings['DEFAULT_WIFI_MODE'] = 'station'
        settings['SSID'] = 'INDINIX'
        settings['SSID_PWD'] = '12345678'
        with open('boot_ini.json', 'w') as input:
            json.dump(settings, input)
        break

if settings['DEFAULT_WIFI_MODE'] == 'station':
    print(start_access_station())
else:
    print('connecting to wifi station')
    print(start_connect_point())

setup_RTC()

