import json
def load_settings():
    with open('boot.ini', 'r') as file:
        return json.load(file)
    
 def map_adc_to_brightness(adc_value):      # Function to map ADC value to lamp brightness
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
        
