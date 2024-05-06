import network
from machine import RTC
import json
import time
from requests import get



with open('boot.ini', 'r') as input:
    settings = json.load(input)


def synchronize_time():
    try:
        response = get("http://worldtimeapi.org/api/ip")
        if response.status_code == 200:
            data = response.json()
            # Extract the datetime string
            datetime_str = data["datetime"]
            # Format: YYYY-MM-DDTHH:MM:SS.nnnnnn±HH:MM
            # Extract the relevant parts
            
            date, time_part = datetime_str.split("T")
            year, month, day = map(int, date.split("-"))
            #print(f'date {date} timepart {time_part}')
            
            time_only, tz = time_part.split("+")
            #print(f"time_only {time_only} tz {tz}")
            hour, minute, second = map(int, time_only[:8].split(":"))
            
            #print(time_only, tz)
            time_tuple = (year, month, day, 0, 0, 0, 0, 0)
            timestamp = time.mktime(time_tuple)
            local_time = time.localtime(timestamp)
            weekday = local_time[6]
            
            # (year, month, day, weekday, hours, minutes, seconds, subseconds)
            rtc = RTC()
            #print(f"year {year}, month {month}, day {day}, hour {hour}, minute {minute}, second {second}")
            rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
            
            year, month, day, weekday, hour, minute, second, subsecond = rtc.datetime()
            weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            print("Current date and time from NTP server:")
            print(f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}, weekday {weekday_names[weekday]} ")
        else:
            raise Exception("Error fetching time")        
    except OSError as e:
        print("Error synchronizing time:", e)
        return False

    return True


def set_rtc_initial_time():
    # Set initial time (replace with desired initial time)
    rtc = RTC()
    initial_time = (2024, 4, 19, 0, 11, 11, 0, 0)
    rtc.datetime(initial_time)
    print("RTC initialized with initial time:", rtc.datetime())


def setup_RTC():
    if not synchronize_time():
        # If synchronization fails, set RTC with initial time
        set_rtc_initial_time()



def start_access_station(SSID=settings['SSID'], password=settings['SSID_PWD']):
   
    ap = network.WLAN(network.AP_IF) # create access-point interface
    ap.active(True)         # activate the interface
    ap.config(essid=SSID, authmode=3, password=password) # SSID of the access point, WPAPSK2
    print(SSID, password)
    ap.config(max_clients=10) # set how many clients can connect to the network
    ip_config = ap.ifconfig()
    print(ap.ifconfig())
    return ap.ifconfig()

def start_connect_point():
    with open('boot.ini', 'r') as input:
        settings = json.load(input)
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(settings['SSID'], settings['SSID_PWD'])
        attemp = 0
        while not wlan.isconnected():
            
            print('trying to connect', attemp)
            attemp += 1
            time.sleep(2)
            if attemp >3:
                print("Can`t connect to WiFi")
                print("setting up default wifi station")

                start_access_station(SSID='INDINIX', password='12345678')                             
                break
    
    return wlan.ifconfig()

