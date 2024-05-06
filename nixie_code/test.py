# Example 1: Using list comprehension
brightness = 200
args = [brightness for _ in range(4)]
print(*args)

# Example 2: Using tuple multiplication
args = (brightness,) * 4  # A tuple with the same value repeated four times
print(args)