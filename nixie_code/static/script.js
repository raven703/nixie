document.getElementById('wifiForm').addEventListener('submit', function(event) {
  event.preventDefault();
  const wifiData = new FormData(this);
  const wifiDataJson = {};
  wifiData.forEach((value, key) => {
    wifiDataJson[key] = value;
  });

  // Replace with your actual backend URL for saving WiFi credentials
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
    console.log('WiFi credentials saved:', data);
  })
  .catch(error => {
    console.error('Error saving WiFi credentials:', error);
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
    console.log('Time settings saved:', data);
  })
  .catch(error => {
    console.error('Error saving time settings:', error);
  });
});


function handleFormSubmitBright(event) {
            event.preventDefault();
            const formData = new FormData(event.target);

            const invalidEntries = Array.from(formData.entries()).filter(([_, value]) => {
                const numValue = parseInt(value, 10);
                return isNaN(numValue) || numValue < 0 || numValue > 1023;
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



function updateLabel(inputElement, labelId) {
    const labelElement = document.getElementById(labelId);
    labelElement.textContent = inputElement.value;
}