from random import choice

def display_digit_effect():

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
        print(choice(effects))

display_digit_effect()