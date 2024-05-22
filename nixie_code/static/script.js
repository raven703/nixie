document.getElementById('wifiForm').addEventListener('submit', function(event) {
  event.preventDefault();
  const wifiData = new FormData(this);
  const wifiDataJson = {};
  wifiData.forEach((value, key) => {
    wifiDataJson[key] = value;
  });

  // Backend URL for saving WiFi credentials
  fetch('/save_wifi', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(wifiDataJson)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    // console.log('WiFi credentials saved:', data);
    alert('WiFi credentials saved: ' + data);
  })
  .catch(error => {
    // console.error('Error saving WiFi credentials:', error);
    alert('Error saving WiFi credentials:', error);
  });
});

document.getElementById('timeForm').addEventListener('submit', function(event) {
  event.preventDefault();
  const timeData = new FormData(this);
  const timeDataJson = {};
  timeData.forEach((value, key) => {
    timeDataJson[key] = value;
  });

  // Replace with your actual backend URL for saving time settings
  fetch('/set_time', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(timeDataJson)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    // console.log('Time settings saved:', data);
    alert('Time settings saved:', data);
  })
  .catch(error => {
    // console.error('Error saving time settings:', error);
    alert('Error saving time settings:', error);
  });
});


function handleFormSubmitBright(event) {
            event.preventDefault();
            const formData = new FormData(event.target);

    const invalidEntries = Array.from(formData.entries()).filter(([name, value]) => {
        if (name !== "autoBright") {
            const numValue = parseInt(value, 10);
            return isNaN(numValue) || numValue < 0 || numValue > 1023;
        }
    });

            if (invalidEntries.length > 0) {
                alert("Please ensure all brightness values are between 0 and 1023.");
                return;
            }

            const brightnessData = Object.fromEntries(formData);

            // Send the brightness data to the backend
            fetch('/set_brightness', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(brightnessData)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Brightness settings saved:', data);
                // alert('Brightness settings updated successfully.');
            })
            .catch(error => {
                console.error('Error saving brightness settings:', error);
                // alert('Failed to update brightness settings.');
            });
        }


document.addEventListener("DOMContentLoaded", function() {
    // Fetch active alarms from the backend and fill the form
    fetch("/get_alarms")
        .then(response => response.json())
        .then(data => {
            for (let i = 1; i <= 4; i++) {
                const alarm = data[`alarm${i}`];
                if (alarm) {
                    document.getElementById(`alarm${i}-time`).value = alarm.time || '';
                    document.getElementById(`alarm${i}-date`).value = alarm.date || '';
                    document.getElementById(`alarm${i}-repeat`).checked = alarm.repeat || false;
                }
            }
        })
        .catch(error => {
            console.error("Error fetching alarms:", error);
        });
      


document.getElementById("alarmForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent default form submission

     // Collect form data
    const alarmsData = {};

    // Collect data for each alarm
    for (let i = 1; i <= 4; i++) {
        const alarmData = {
            time: document.getElementById(`alarm${i}-time`).value,
            date: document.getElementById(`alarm${i}-date`).value,
            repeat: document.getElementById(`alarm${i}-repeat`).checked
        };
        alarmsData[`alarm${i}`] = alarmData;
    }

    // Send data to the server
    fetch("/set_alarms", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(alarmsData)
    })
    .then(response => {
        if (response.ok) {
            console.log("Alarms set successfully");
            alert("Alarms set successfully");
        } else {
            // console.error("Failed to set alarms");
            alarm("Failed to set alarms");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
});

});

function updateLabel(inputElement, labelId) {
    const labelElement = document.getElementById(labelId);
    labelElement.textContent = inputElement.value;
}
