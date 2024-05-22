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
        




from microdot import Microdot, send_file, Response #, Request
from wifinet import synchronize_time as sync_time
import asyncio

import json

from machine import Pin, PWM, RTC, ADC, Pin
from utils import *
from config import Config
from buzzerplayer import BuzzerPlayer
import time
import random
from nixie_lamps import NixieLamp
#import _thread  # MicroPython threading
import gc


# Initialize ADC on GPIO34
adc_pin = 34  # GPIO34
adc = ADC(Pin(adc_pin))
# Set the attenuation (optional, determines voltage range)
adc.atten(ADC.ATTN_11DB)

rtc=RTC()
app = Microdot()
lamp_nix = NixieLamp(brightness=612) # prepare Nixie class, 200 duty cycle, brightness


led_pin = 23
blink_led = PWM(Pin(led_pin), freq=1000, duty=512)
PERIOD = 2


# set brightness level from settings
settings = load_settings()
config = Config()

#initiate buzzer class

buzzer = BuzzerPlayer(4)  # Change 4 to the pin number connected to your buzzer

#buzzer.play(buzzer.IMPERIAL_MARCH_MELODY, 10000)  # Play the Star Wars main theme for 5 seconds
#time.sleep(1)
buzzer.play(buzzer.SHORT_BEEP, 1000)  
buzzer.stop()

app = Microdot()



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

@app.route('/get_alarms', methods=['GET'])
async def get_alarms(request):
    alarms = config.ALARMS
    return Response(alarms, headers={'Content-Type': 'application/json'})



@app.route('/set_alarms', methods=['GET', 'POST'])
async def set_alarms(request):
    async def display_alarm_number(binary_number):
        await asyncio.sleep(1)
        if binary_number == '0000':
            lamp_nix.display_number(binary_number, flash=True)
        else:
            lamp_nix.display_number(bin(binary_number)[2:], flash=True)
    
    alarms = request.json
    
    all_alarms = {"alarm1": alarms.get("alarm1", 0),
              "alarm2": alarms.get("alarm2", 0),
              "alarm3": alarms.get("alarm3", 0),
              "alarm4": alarms.get("alarm4", 0),}
    print('alarm set:', all_alarms)
    config.update_config(ALARMS = all_alarms)
    
    binary_number = 0b0000
    # Iterate over alarm_configs and set the corresponding bit to 1 if 'time' is not empty
    for i in range(1, 5):
        alarm_key = f'alarm{i}'
        if all_alarms[alarm_key]['time']:
            binary_number |= 1 << (4 - i)  # Set the corresponding bit to 1
    # Ensure binary_number is 0b0000 if it is 0b0
    if binary_number == 0:        
        binary_number = '0000'
    
     # Schedule the async display function
    asyncio.create_task(display_alarm_number(binary_number))
    # return Response('', 204)
    #time.sleep(2)
    
    
    
    
    
    
    



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

async def show_time():
     pwm_lamp_pins = lamp_nix.pwm_lamp_pins
     lamp_0_pwm = lamp_nix.pwm_lamp_pins[0]
     lamp_1_pwm = lamp_nix.pwm_lamp_pins[1]
     lamp_2_pwm = lamp_nix.pwm_lamp_pins[2]
     lamp_3_pwm = lamp_nix.pwm_lamp_pins[3]

     lamp_nix.display_number('2024') # in string
     current_time = rtc.datetime()
     hour = current_time[4]
     minute = current_time[5]
     second = current_time[6]
     print(f"@from async: Current time (hr:min): {hour:02d}:{minute:02d}")
      
     random_number_interval = 10 * 60  # 10 minutes in seconds to show random effects
     random_number_timer = random_number_interval
     
   
     while True:
         current_hour = time.localtime()[3]  # Get the current hour
         if current_hour == 23:
             sync_time()
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
             # check alarm
             if config.check_alarm():
                 print('play sound')
                 buzzer.play(buzzer.IMPERIAL_MARCH_MELODY, 10000)
                 
             await asyncio.sleep(6)
             random_number_timer -= 6
             
         for _ in range(7):  # Wait for 5 seconds
             current_time = rtc.datetime()
             seconds = current_time[6]
             lamp_nix.display_seconds(f'00{seconds:02d}')
             #print(f'00{seconds:02d}')
             await asyncio.sleep(1)
             random_number_timer -= 6
             
         if random_number_timer <= 0:
            lamp_nix.display_digit_effect() 
            random_number_timer = random_number_interval
             

async def show_blink_led():
    blink_led.freq(1000)
    
   
    def calculate_duty_cycle(period): # function calculates the duty cycle of the PWM signal based on the current time and the specified period. 
        # Calculate the duty cycle as a percentage
        duty_cycle = 100 * (1 - abs((time.time() % period) / period - 0.5) * 2)
        return int(duty_cycle * 5.23)  # Convert percentage to 0-1023 range

    while True:
        current_hour = time.localtime()[3]  # Get the current hour
        if 23 <= current_hour or current_hour < 6:
            blink_led.duty(0)  # Turn off the LED
        else:
            duty_cycle = calculate_duty_cycle(PERIOD)
            blink_led.duty(duty_cycle)
        await asyncio.sleep(1)  # Adjust the sleep time for smoother transition
        
        
        

gc.collect()
print(f'Memory free: {gc.mem_free()}')



async def start_server():
    try:
        await app.start_server(port=80, debug=True)
    except OSError as e:
        print(f"Failed to start server: {e}")
        


async def main():
    # Run the Microdot web server in the background
    server_task = asyncio.create_task(start_server())
    # Run the show_time function concurrently
    show_time_task = asyncio.create_task(show_time())
    blink_led_task = asyncio.create_task(show_blink_led())
   
    # Wait for all tasks to complete
    await asyncio.gather(server_task, show_time_task, blink_led_task)
    

# Start the asyncio event loop
asyncio.run(main())
    


