import json
import machine
import utime

class Config:
    def __init__(self):
        with open("boot.ini") as f:
            config_data = json.load(f)
        
        self.SSID_PWD = config_data["SSID_PWD"]
        self.AUTO_BRIGHT = config_data["AUTO_BRIGHT"]
        self.BRIGHTNESS_LEVELS = config_data["BRIGHTNESS_LEVELS"]
        self.DEFAULT_WIFI_MODE = config_data["DEFAULT_WIFI_MODE"]
        self.SSID = config_data["SSID"]
        self.TIMEZONE = config_data["TIMEZONE"]
        self.ALARMS = config_data["ALARMS"]
        self.PLAY_ALARM = False 


        
        self.rtc = machine.RTC()


    # Function to calculate time difference and trigger alarm
    def trigger_alarm(self, alarm_name, alarm_data):
        alarm_time = alarm_data['time']
        alarm_date = alarm_data['date']
        repeat_alarm = alarm_data['repeat']
        if not alarm_time or not alarm_date:
            return
        
        current_time = utime.time()
        alarm_datetime = utime.mktime((int(alarm_date[:4]), int(alarm_date[5:7]), int(alarm_date[8:10]), int(alarm_time[:2]), int(alarm_time[3:]), 0, 0, 0))
        time_difference = alarm_datetime - current_time
        
       
        #print('alarm_name ', alarm_name)
        #print('alarm_time ',alarm_time)
        #print('alarm_date ',alarm_date)
        #print('repeat_alarm',repeat_alarm)
    
        if time_difference <= 0 and not repeat_alarm:
            print(f"Triggering alarm {alarm_name} now!")
            self.PLAY_ALARM = True
            self.ALARMS[alarm_name]["time"] = ""
            self.save_config()
            return True 
            
            # Code to trigger alarm goes here
        if time_difference <= 0 and repeat_alarm:
            # Assuming alarm repeats every day for simplicity
            tomorrow = utime.localtime(current_time + 86400)
            next_alarm_date = "{:04d}-{:02d}-{:02d}".format(tomorrow[0], tomorrow[1], tomorrow[2])
            alarm_data['date'] = next_alarm_date
            #print("Alarm", alarm_name, "will repeat on", next_alarm_date)
            self.ALARMS[alarm_name]["date"] = next_alarm_date
            self.save_config()
            self.PLAY_ALARM = True
            return True 
               
        return False 
            
            #print("Alarm", alarm_name, "will trigger in", time_difference, "seconds.")

            
            
            
    def check_alarm(self):
        # Loop through alarms and trigger if not empty
        result =[]
        for alarm_name, alarm_data in self.ALARMS.items():
            if alarm_data["time"] and alarm_data["date"]:
                #alarm_time = f"{alarm_data['date']} {alarm_data['time']}"
                if self.trigger_alarm(alarm_name, alarm_data):
                    return True
        return False 
                
                

            
        
        
    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if key == "BRIGHTNESS_LEVELS":                
                self.BRIGHTNESS_LEVELS.update(value)
            elif key == "ALARMS":
                self.ALARMS.update(value)                
            else:
                setattr(self, key, value)
        self.save_config()

    def save_config(self):
        with open("boot.ini", "w") as f:
            json.dump({
                "SSID_PWD": self.SSID_PWD,
                "AUTO_BRIGHT": self.AUTO_BRIGHT,
                "BRIGHTNESS_LEVELS": self.BRIGHTNESS_LEVELS,
                "DEFAULT_WIFI_MODE": self.DEFAULT_WIFI_MODE,
                "SSID": self.SSID,
                "TIMEZONE": self.TIMEZONE,
                "ALARMS": self.ALARMS
            }, f)


