from microdot import Microdot, send_file, Response, Request
import json

from machine import Pin, PWM, RTC, ADC
from utils import *
import time
import random

from nixie_lamps import NixieLamp
import asyncio
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
brightness_levels = settings.get("BRIGHTNESS_LEVELS", {})
# Ensure you have all four brightness values to pass to set_brightness
lamp_values = [brightness_levels.get(f"lamp{i}", 0) for i in range(1, 5)]
# Check that the extracted list has 4 elements
if len(lamp_values) != 4:
    raise ValueError("Expected 4 lamp brightness levels.")
# Use the list unpacking to pass the values to set_brightness
lamp_nix.set_brightness(*lamp_values)



    


@app.route('/')
async def index(request):
    return send_file('index.html')

@app.route('/static/<path:path>')
async def static(request, path):
    if '..' in path:
        # directory traversal is not allowed
        return 'Not found', 404
    return send_file('static/' + path, max_age=86400)

@app.route('/save_wifi', methods=['GET', 'POST'])
async def save_wifi(request):
    credentials = request.json
    print(credentials)
    with open("boot.ini", "r+") as file:
        settings = json.load(file)
        settings["DEFAULT_WIFI_MODE"] = "POINT"
        settings["SSID"] = credentials.get('ssid')
        settings["SSID_PWD"] = credentials.get('pwd')
            # Go back to the beginning of the file
        file.seek(0)
        # Write the updated settings to the file
        json.dump(settings, file)
        # Ensure the rest of the file is empty after writing
        file.truncate()
 
        
    return {'WiFi_cred': 'saved'}



@app.route('/set_brightness', methods=['GET', 'POST'])
async def set_brightness(request):
    brightness_levels = request.json
    print(brightness_levels)
    config_data={}
    with open('boot.ini', 'r') as file:
        settings = json.load(file)
        config_data = {
            "DEFAULT_WIFI_MODE": settings['DEFAULT_WIFI_MODE'],
            "SSID": settings['SSID'],
            "SSID_PWD": settings['SSID_PWD'],
            "TIMEZONE": settings['TIMEZONE'],
            # Include the brightness levels for 4 lamps
            "BRIGHTNESS_LEVELS": {
                "lamp1": brightness_levels.get("lamp1", 0),
                "lamp2": brightness_levels.get("lamp2", 0),
                "lamp3": brightness_levels.get("lamp3", 0),
                "lamp4": brightness_levels.get("lamp4", 0),
                },
        }
    with open('boot.ini', 'w') as file:
        # Write the JSON data to the file
        json.dump(config_data, file)
    lamp_nix.set_brightness(brightness_levels.get("lamp1", 0),
                            brightness_levels.get("lamp2", 0),
                            brightness_levels.get("lamp3", 0),
                            brightness_levels.get("lamp4", 0))

    return {'brightness': 'saved'}




@app.route('/set_time', methods=['GET', 'POST'])
async def set_time(request):
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



async def show_time():
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
        adc_min = 0
        adc_max = 2600
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
     
     await asyncio.sleep_ms(2000)

     while True:
         for _ in range(10):  # Display current time for 1 minute
             current_time = rtc.datetime()
             hour = current_time[4]
             minute = current_time[5]
             seconds = current_time[6]
             formatted_time = f'{hour:02d}{minute:02d}'
             #print(formatted_time)
             lamp_nix.display_number(formatted_time)
             # Read ADC value from photo resistor
             adc_value = adc.read()  # This will return a value from 0 to 4095
             brightness = map_adc_to_brightness(adc_value)  # Get corresponding brightness
             
             lamp_nix.set_brightness(brightness, brightness, brightness, brightness)

             #print("ADC value:", adc_value)
             #print('brightness', brightness)
             
             await asyncio.sleep(6)
             
         for _ in range(7):  # Wait for 5 seconds
             current_time = rtc.datetime()
             seconds = current_time[6]
             lamp_nix.display_seconds(f'00{seconds:02d}')
             print(f'00{seconds:02d}')
             await asyncio.sleep(1)
             
async def show_random_number():
    while True:
        lamp_nix.display_digit_effect()     
        await asyncio.sleep(120)


gc.collect()
#print(gc.mem_free())



async def main():
    task1 = asyncio.create_task(show_random_number())
    task2 = asyncio.create_task(show_time())
    task3 = asyncio.create_task(app.run(port=80, debug=True))
    
    await task1
    await task2
    await task3
 
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state
    
