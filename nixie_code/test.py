import json
from datetime import datetime, timedelta

# Parse JSON string
json_str = '{"ALARMS": {"alarm2": {"time": "", "date": "", "repeat": false}, "alarm3": {"time": "", "date": "", "repeat": false}, "alarm4": {"time": "", "date": "", "repeat": false}, "alarm1": {"time": "11:11", "date": "2024-05-15", "repeat": true}}}'
data = json.loads(json_str)

# Function to calculate time difference and trigger alarm
def trigger_alarm(alarm_name, alarm_time):
    current_time = datetime.now()
    alarm_datetime = datetime.strptime(alarm_time, "%Y-%m-%d %H:%M")
    time_difference = alarm_datetime - current_time
    if time_difference.total_seconds() <= 0:
        print(f"Triggering alarm {alarm_name} now!")
        # Code to trigger alarm goes here
    else:
        print(f"Alarm {alarm_name} will trigger in {time_difference.total_seconds()} seconds.")

# Loop through alarms and trigger if not empty
for alarm_name, alarm_data in data["ALARMS"].items():
    if alarm_data["time"] and alarm_data["date"]:
        alarm_time = f"{alarm_data['date']} {alarm_data['time']}"
        trigger_alarm(alarm_name, alarm_time)
