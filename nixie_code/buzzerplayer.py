from machine import Pin, PWM
import time

class BuzzerPlayer:
    # Define the frequencies for the notes (Hz)
    NOTES = {
    '00': 01,
    'C0': 16, 'C#0': 17, 'D0': 18, 'D#0': 19, 'E0': 20, 'F0': 21, 'F#0': 23, 'G0': 24, 'G#0': 26, 'A0': 27, 'A#0': 29, 'B0': 31,
    'C1': 33, 'C#1': 35, 'D1': 37, 'D#1': 39, 'E1': 41, 'F1': 44, 'F#1': 46, 'G1': 49, 'G#1': 52, 'A1': 55, 'A#1': 58, 'B1': 62,
    'C2': 65, 'C#2': 69, 'D2': 73, 'D#2': 78, 'E2': 82, 'F2': 87, 'F#2': 92, 'G2': 98, 'G#2': 104, 'A2': 110, 'A#2': 117, 'B2': 124,
    'C3': 131, 'C#3': 139, 'D3': 147, 'D#3': 156, 'E3': 165, 'F3': 175, 'F#3': 185, 'G3': 196, 'G#3': 208, 'A3': 220, 'A#3': 233, 'B3': 247,
    'C4': 262, 'C#4': 277, 'D4': 294, 'D#4': 311, 'E4': 330, 'F4': 349, 'F#4': 370, 'G4': 392, 'G#4': 415, 'A4': 440, 'A#4': 466, 'B4': 494,
    'C5': 523, 'C#5': 554, 'D5': 587, 'D#5': 622, 'E5': 659, 'F5': 698, 'F#5': 740, 'G5': 784, 'G#5': 831, 'A5': 880, 'A#5': 932, 'B5': 988,
    'C6': 1046, 'C#6': 1109, 'D6': 1175, 'D#6': 1244, 'E6': 1318, 'F6': 1397, 'F#6': 1480, 'G6': 1568, 'G#6': 1661, 'A6': 1760, 'A#6': 1865, 'B6': 1976,
    'C7': 2093, 'C#7': 2217, 'D7': 2349, 'D#7': 2489, 'E7': 2637, 'F7': 2794, 'F#7': 2960, 'G7': 3136, 'G#7': 3322, 'A7': 3520, 'A#7': 3729, 'B7': 3951,
    'C8': 4186, 'C#8': 4435, 'D8': 4699, 'D#8': 4978, 'E8': 5274, 'F8': 5588, 'F#8': 5920, 'G8': 6272, 'G#8': 6645, 'A8': 7040, 'A#8': 7458, 'B8': 7902
}
    
    SHORT_BEEP = [('D4', 1000)]
    
    
        # Define the Imperial March melody
    IMPERIAL_MARCH_MELODY = [
               
        ('D4', 100), ('F#4', 100), ('00', 100), ('G4', 100), ('00', 100), ('A4', 100), ('00', 300),
        ('D5', 200), ('00', 100), ('B4', 200), ('00', 300),
        ('D4', 100), ('F#4', 100), ('00', 100), ('G4', 100), ('00', 100), ('A4', 100), ('00', 100), ('A4', 100), ('00', 100),
        ('D5', 200), ('00', 100), ('B4', 200), ('00', 300),
        ('D4', 100), ('F#4', 100), ('00', 100), ('G4', 100), ('00', 100), ('A4', 100), ('00', 300),
        ('D5', 200), ('00', 100), ('B4', 200), ('00', 300),
        ('F#5', 100), ('00', 100), ('G5', 100), ('00', 100), ('A5', 100), ('00', 100), ('D5', 100), ('00', 100),
        ('D5', 100), ('E5', 100), ('F#5', 100), ('E5', 100),
        ('00', 1000)]
        
        
    
    
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT)
        self.pwm = PWM(self.pin)

    def play_tone(self, frequency, duration):
        self.pwm.duty(512)
        self.pwm.freq(frequency)
        #self.pwm.duty(512)
        time.sleep_ms(duration)
        
        
    def play(self, melody, duration):
        total_duration = 0
        for note, note_duration in melody:
            if total_duration + note_duration > duration:
                break
            self.play_tone(self.NOTES[note], note_duration)
            total_duration += note_duration
        self.pwm.duty(0)       
        
    def stop(self):
        #self.pwm.deinit()
        self.pwm.duty(0)
        





def play_imperial_march(self, buzzer, duration_limit):
    total_duration = 0
    for note, duration in IMPERIAL_MARCH_MELODY:
        if total_duration + duration > duration_limit:
            break
        buzzer.play_tone(NOTES[note], duration)
        total_duration += duration


