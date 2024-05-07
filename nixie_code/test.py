ip_addr = '192.168.4.1'
ip_parts = [int(part) for part in ip_addr.split('.')]  # Convert each part to an integer

print(ip_parts)  # Output: [192, 168, 4, 1]
