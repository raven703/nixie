alarm_configs = {
    'alarm2': {'time': '', 'date': '', 'repeat': False},
    'alarm3': {'time': '15:03', 'date': '', 'repeat': False},
    'alarm4': {'time': '', 'date': '', 'repeat': False},
    'alarm1': {'time': '15:03', 'date': '2024-05-20', 'repeat': False}
}

binary_number = 0b0000

# Iterate over alarm_configs and set the corresponding bit to 1 if 'time' is not empty
for i in range(1, 5):
    alarm_key = f'alarm{i}'
    if alarm_configs[alarm_key]['time']:
        binary_number |= 1 << (4 - i)  # Set the corresponding bit to 1

print("Binary Number:", bin(binary_number))
