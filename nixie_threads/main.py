# all pins:
#adc_pin = 34  # GPIO34adc_pin = 34  # GPIO34
#pwm_lamp_pins = [
#                 PWM(Pin(18), freq=1000, duty=brightness),
#                 PWM(Pin(19), freq=1000, duty=brightness),
#                 PWM(Pin(25), freq=1000, duty=brightness),
#                 PWM(Pin(26), freq=1000, duty=brightness),]
#  ser = Pin(33, Pin.OUT)
#  rclk = Pin(32, Pin.OUT)
#  srclk = Pin(27, Pin.OUT) 
#  srclr = Pin(14, Pin.OUT, value=1) # pulsing low clears data
        




from microdot1 import Microdot, send_file, Response, Request
import json

from machine import Pin, PWM, RTC, ADC
from utils import *
from config import Config
import time
#import random
from nixie_lamps import NixieLamp
import _thread  # MicroPython threading
import gc


# Initialize ADC on GPIO34
adc_pin = 34  # GPIO34
adc = ADC(Pin(adc_pin))
# Set the attenuation (optional, determines voltage range)
adc.atten(ADC.ATTN_11DB)

rtc=RTC()
app = Microdot()
lamp_nix = NixieLamp(brightness=612) # prepare Nixie class, 200 duty cycle, brightness


# set brightness level from settings
settings = load_settings()
config = Config()

brightness_levels = config.BRIGHTNESS_LEVELS
# Ensure you have all four brightness values to pass to set_brightness
lamp_values = [brightness_levels.get(f"lamp{i}", 0) for i in range(1, 5)]
# Check that the extracted list has 4 elements
if len(lamp_values) != 4:
    raise ValueError("Expected 4 lamp brightness levels.")
# Use the list unpacking to pass the values to set_brightness
lamp_nix.set_brightness(*lamp_values)


@app.route('/')
def index(request):
    return send_file('index.html')

@app.route('/static/<path:path>')
def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path, max_age=86400)

@app.route('/save_wifi', methods=['GET', 'POST'])
def save_wifi(request):
    credentials = request.json
     
    config.update_config(DEFAULT_WIFI_MODE = "POINT",
                             SSID = credentials.get('ssid'),
                             SSID_PWD = credentials.get('pwd'),
                             )
    return {'WiFi_cred': 'saved'}



@app.route('/set_brightness', methods=['GET', 'POST'])
def set_brightness(request):
    brightness_levels = request.json
   
    lamp_nix.set_brightness(brightness_levels.get("lamp1", 0),
                            brightness_levels.get("lamp2", 0),
                            brightness_levels.get("lamp3", 0),
                            brightness_levels.get("lamp4", 0))
    
    new_brightness_levels = {"lamp1": brightness_levels.get("lamp1", 0),
                             "lamp2": brightness_levels.get("lamp2", 0),
                             "lamp3": brightness_levels.get("lamp3", 0),
                             "lamp4": brightness_levels.get("lamp4", 0),
                             }
    
    autoBright=''
    
    if brightness_levels.get('autoBright') is not None:
        autoBright = "True"
    else:
        autoBright = "False"
        
    config.update_config(BRIGHTNESS_LEVELS=new_brightness_levels,
                         AUTO_BRIGHT = autoBright)
    #print(brightness_levels.get('autoBright'))
    
    return {'brightness': 'saved'}


@app.route('/set_time', methods=['GET', 'POST'])
def set_time(request):
    current_time = request.json
    user_time = current_time.get('time', '22:22')
    user_date = current_time.get('date', '1984-01-01')
    timezone_offset = current_time.get('tmz', 0)  # Default to 0 if not provided
    rtc = RTC()
    try:
        # Parse the user date and time
        year, month, day = map(int, user_date.split('-'))
        hour, minute = map(int, user_time.split(':'))
                                # Validate parsed values
        if not (1 <= month <= 12):
            raise ValueError("Month out of range")
        if not (1 <= day <= 31):
            raise ValueError("Day out of range")
        if not (0 <= hour < 24):
            raise ValueError("Hour out of range")
        if not (0 <= minute < 60):
            raise ValueError("Minute out of range")
        # Set the RTC with the provided time and date
        rtc.datetime((year, month, day, 0, hour, minute, 0, 0))  # weekday and subseconds are optional
    except (ValueError, AttributeError) as e:
        print("Invalid user-provided date or time:", e)
        # Optionally, you could set a default fallback time here
        rtc.datetime((1984, 1, 1, 0, 0, 0, 0, 0))
            

    # Apply the timezone offset
    if timezone_offset:
                # Adjust the RTC for the timezone offset in hours
        current_rtc = list(rtc.datetime())
        timezone_offset_hours = int(timezone_offset)

        # Adjust hours by the timezone offset
        current_rtc[4] += timezone_offset_hours

        # Normalize the RTC datetime in case of overflow/underflow
        current_rtc[3] = (rtc.datetime()[3] + current_rtc[4] // 24) % 7  # Adjust weekday
        current_rtc[4] %= 24  # Keep hours in the range 0-23

        # Update the RTC with the new time
        rtc.datetime(tuple(current_rtc))
  
    return {'Time': 'saved'}


# Thread functions

def show_time():
     pwm_lamp_pins = lamp_nix.pwm_lamp_pins
     lamp_0_pwm = lamp_nix.pwm_lamp_pins[0]
     lamp_1_pwm = lamp_nix.pwm_lamp_pins[1]
     lamp_2_pwm = lamp_nix.pwm_lamp_pins[2]
     lamp_3_pwm = lamp_nix.pwm_lamp_pins[3]

     lamp_nix.display_number('2024') # in string
     print('duty is', lamp_0_pwm.duty())
     print('duty is', lamp_1_pwm.duty())
     print('duty is', lamp_2_pwm.duty())
     print('duty is', lamp_3_pwm.duty())
     # Get current RTC time
     current_time = rtc.datetime()
     hour = current_time[4]
     minute = current_time[5]
     second = current_time[6]
     print(f"@from async: Current time (hr:min): {hour:02d}:{minute:02d}")
     
     # Function to map ADC value to lamp brightness
     def map_adc_to_brightness(adc_value):
        # ADC range is 0 to 2600
        # Lamp brightness range is 100 to 1023
        # Linear mapping formula
        adc_min = 1800
        adc_max = 4096
        brightness_min = 50
        brightness_max = 1023

        # Calculate brightness based on ADC value
        if adc_value < adc_min:
            adc_value = adc_min
        elif adc_value > adc_max:
            adc_value = adc_max
           # Interpolate to get the corresponding brightness value
        brightness = brightness_min + (adc_value - adc_min) * (brightness_max - brightness_min) / (adc_max - adc_min)
    
        return int(brightness)  # Ensure it's an integer
     
     while True:
         for _ in range(10):  # Display current time for 1 minute
             current_time = rtc.datetime()
             hour = current_time[4]
             minute = current_time[5]
             seconds = current_time[6]
             formatted_time = f'{hour:02d}{minute:02d}'
             lamp_nix.display_number(formatted_time)
             # Read ADC value from photo resistor
             adc_value = adc.read()  # This will return a value from 0 to 4095
             
             if config.AUTO_BRIGHT == 'True':
                 brightness = map_adc_to_brightness(adc_value)  # Get corresponding brightness
                 lamp_nix.set_brightness(brightness, brightness, brightness, brightness)
                 
             else:
                 pass
             time.sleep(6)
             
         for _ in range(7):  # Wait for 5 seconds
             current_time = rtc.datetime()
             seconds = current_time[6]
             lamp_nix.display_seconds(f'00{seconds:02d}')
             print(f'00{seconds:02d}')
             time.sleep(1)
             
def show_random_number():
    while True:
        lamp_nix.display_digit_effect()     
        time.sleep(120)


gc.collect()
print(gc.mem_free())

# Start the threads
_thread.start_new_thread(show_time, ())
_thread.start_new_thread(show_random_number, ())

# Start the Microdot web server
app.run(port=80, debug=True)



    
