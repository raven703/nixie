import machine
from random import randint, choice
from machine import Pin, PWM
import time
from sr74hc595_bitbang import SR74HC595_BITBANG

class NixieLamp:
    def __init__(self, brightness=512) -> None: # shift for digit codes
        
        self.digits_codes = [
            0b1000_0000_0000_0000_0000_0000_0000_0000_0000_0000,  # Digit 0
            0b0100_0000_0000_0000_0000_0000_0000_0000_0000_0000,  # Digit 1
            0b0010_0000_0000_0000_0000_0000_0000_0000_0000_0000,  # Digit 2
            0b0001_0000_0000_0000_0000_0000_0000_0000_0000_0000,  # Digit 3
            0b0000_1000_0000_0000_0000_0000_0000_0000_0000_0000,  # Digit 4
            0b0000_0100_0000_0000_0000_0000_0000_0000_0000_0000,  # Digit 5
            0b0000_0010_0000_0000_0000_0000_0000_0000_0000_0000,  # Digit 6
            0b0000_0001_0000_0000_0000_0000_0000_0000_0000_0000,  # Digit 7
            0b0000_0000_1000_0000_0000_0000_0000_0000_0000_0000,  # Digit 8
            0b0000_0000_0100_0000_0000_0000_0000_0000_0000_0000,  # Digit 9
            0b0000_0000_0000_0000_0000_0000_0000_0000_0000_0000,  # Digit 10, no digit
        ]
        self.no_digit =  0b0000_0000_0000_0000_0000_0000_0000_0000_0000_0000 # display nothing
        self.num_bits = 40 # number of bits to send. For 5 shift registers this number is 40 (8 bits for each)
        
        # setup pins and PWM mode 
        self.pwm_lamp_pins = [
                 PWM(Pin(18), freq=2000, duty=brightness),
                 PWM(Pin(19), freq=2000, duty=brightness),
                 PWM(Pin(25), freq=2000, duty=brightness),
                 PWM(Pin(26), freq=2000, duty=brightness),
                ]
        self.brightness = brightness
        self.brightness_max = 1023
        self.brightness_normal = 512
        self.brightness_min = 0

        ser = Pin(33, Pin.OUT)
        rclk = Pin(32, Pin.OUT)
        srclk = Pin(27, Pin.OUT) 
        srclr = Pin(14, Pin.OUT, value=1) # pulsing low clears data

        self.sr = SR74HC595_BITBANG(ser, srclk, rclk, srclr) #instanciate class for shift register
        self.sr.clear()

        self.lamp_0_shift = 0
        self.lamp_1_shift = 10
        self.lamp_2_shift = 20
        self.lamp_3_shift = 30

        self.display_off()

    def get_digit_code(self, digit, shift):
        if digit < 0 or digit > 10:
            raise ValueError("Digit must be between 0 and 9")
        if digit == 10:
            binary_string = bin(self.digits_codes[10] >> shift)[2:]
            formatted_output = '0b' + '0' * (40 - len(binary_string)) + binary_string
            return str(formatted_output)
        
        binary_string = bin(self.digits_codes[digit] >> shift)[2:]
        # Add leading zeros to ensure the string has a length of 40 characters
        formatted_output = '0b' + '0' * (40 - len(binary_string)) + binary_string
        return str(formatted_output)
    
    

    def display_digit(self, digit, lamp_number=0):
        if digit < 0 or digit > 9:
            raise ValueError("Digit must be between 0 and 9")
        
        lamp_shift_attr = f"lamp_{lamp_number}_shift"
        
        # Get the shift value using getattr
        lamp_shift = getattr(self, lamp_shift_attr, None)
        if lamp_shift is None:
            raise ValueError(f"Invalid lamp number: {lamp_number}")
        
        binary_string = bin(self.digits_codes[digit] >> lamp_shift)[2:]
        
        # Add leading zeros to ensure the string has a length of 40 characters
        formatted_output = '0b' + '0' * (40 - len(binary_string)) + binary_string
        result = str(formatted_output)
        hex_value = int(binary_string, 2)
        self.sr.bits(hex_value, self.num_bits, 1)
        return True
    
    def display_off(self): # send 40 bits to close all shift registers
        self.sr.bits(0b0000_0000_0000_0000_0000_0000_0000_0000_0000_0000,
                     self.num_bits, 1)
    

    def display_seconds(self, number):
         digits = [int(i) for i in str(number)]
         int_0 = int(self.get_digit_code(10, self.lamp_0_shift), 2)
         int_1 = int(self.get_digit_code(10, self.lamp_1_shift), 2)
         int_2 = int(self.get_digit_code(digits[2], self.lamp_2_shift), 2)
         int_3 = int(self.get_digit_code(digits[3], self.lamp_3_shift), 2)
         result = int_0 | int_1 | int_2 | int_3
         self.sr.bits(result, self.num_bits, 1)
         return True

    def display_number(self, number):        
        digits = [int(i) for i in str(number)]
        
        int_0 = int(self.get_digit_code(digits[0], self.lamp_0_shift), 2)
        int_1 = int(self.get_digit_code(digits[1], self.lamp_1_shift), 2)
        int_2 = int(self.get_digit_code(digits[2], self.lamp_2_shift), 2)
        int_3 = int(self.get_digit_code(digits[3], self.lamp_3_shift), 2)
        

        if digits[0] == 0:
            int_0 = int(self.get_digit_code(10, self.lamp_0_shift), 2)
            
        result = int_0 | int_1 | int_2 | int_3
        
        self.sr.bits(result, self.num_bits, 1)
        return True
    
    def display_digit_effect(self):

        def show_digit_slide():
            digit=0
            while True:
                for lamp_number in range(4):
                    self.display_digit(digit, lamp_number)
                    time.sleep(0.05)
                digit += 1
                if digit >9:
                    break
      
        def show_random_number():
            for _ in range(5):
                random_number = randint(1000, 9999)
                self.display_number(str(random_number))
                # print(random_number)
                time.sleep(0.1)  # Display random number for 5 seconds
        
        def show_digit_count():
          
            # List to collect outputs
            output_list = []
            # Initial digits
            d1, d2, d3, d4 = 0, 0, 0, 0
            # Increment d1 and adjust other digits if needed
            while d1 < 9:
                output_list.append(f'{d1}{d2}{d3}{d4}')
                d1 += 1
            # Adjust other digits based on specific logic
                if d1 - d2 >= 2:
                    d2 += 1
                if d2 - d3 >= 2:
                    d3 += 1
                if d3 - d4 >= 2:
                    d4 += 1

        # Continue incrementing other digits if needed
            while d2 < 9 or d3 < 9 or d4 < 9:
                if d2 < 9:
                    d2 += 1
                if d3 < 9:
                    d3 += 1
                if d4 < 9:
                    d4 += 1
                # Add to output list
                output_list.append(f'{d1}{d2}{d3}{d4}')
                
                for number in output_list:
                    self.display_number(number)
                    time.sleep(0.1)
   
        effects = [show_digit_slide, show_random_number, show_digit_count]
        choice(effects)()
        
        
        return True 

    
    def set_lamps_normal(self, brightness): # set Brightness level / PWM duty  normal 50%
        for lamp in self.pwm_lamp_pins:
            lamp.duty(self.brightness_normal)

    def set_brightness(self, *args):
        num_lamps = len(self.pwm_lamp_pins)
        # Ensure the number of arguments matches the number of PWM lamps
        if len(args) != num_lamps:
            raise ValueError(f"Expected {num_lamps} arguments, but got {len(args)}.")
        # Validate that each argument is within the range 0 to 1023
        for i, arg in enumerate(args):
            if not (0 <= int(arg) <= 1023):
                raise ValueError(f"Argument at index {i} is out of range (0-1023). Got: {arg}.")
        # Iterate through the PWM lamps and the brightness values
        for pwm, brightness in zip(self.pwm_lamp_pins, args):
            
            pwm.duty(int(brightness))
            #print(pwm.duty())
       
    
    def set_lamps_max(self):                # set Brightness level / PWM duty 100%
        for lamp in self.pwm_lamp_pins:
            lamp.duty(self.brightness_max)  
    
    
    def set_lamps_off(self):                # set Brightness  / PWM duty 0%
        for lamp in self.pwm_lamp_pins:
            lamp.duty(self.brightness_min)   

        
 
        
        