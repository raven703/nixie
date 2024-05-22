# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import webrepl
webrepl.start()
from wifinet import *
from machine import Pin, RTC, freq
import time
from nixie_lamps import NixieLamp
import esp32

lamp_nix = NixieLamp() # prepare Nixie class

with open('boot.ini', 'r') as input:
    settings = json.load(input)
    
def display_ip_address(ip_addr):
    ip_parts = [int(part) for part in ip_addr.split('.')]  # Convert each part to an integer
    formatted_parts = [f"{octet:04d}" for octet in ip_parts]
    
    for digit in formatted_parts:
        lamp_nix.display_number(f'{digit}') # in string
        time.sleep(1.3)
    

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
    ip_addr = start_access_station()
    print('from boot1 ', ip_addr)
    display_ip_address(ip_addr)
        
    
else:
    print('connecting to wifi station')
    ip_addr = start_connect_point()
    print('from boot2 ', ip_addr)
    display_ip_address(ip_addr)
    
    

setup_RTC()
# Disable WiFi sleep mode
esp32.wake_on_ext0(pin = None, level = 0)
# Set CPU frequency to maximum to disable modem sleep
#freq(240000000)
# If you want to disable the modem sleep as well
#esp32.set_modem_sleep(0)
