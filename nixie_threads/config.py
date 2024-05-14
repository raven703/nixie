import json

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
        
    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            if key == "BRIGHTNESS_LEVELS":
                
                self.BRIGHTNESS_LEVELS.update(value)
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
                "TIMEZONE": self.TIMEZONE
            }, f)


