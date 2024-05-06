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
        event.preventDefault(); // Prevent the form from refreshing the page

        const form = document.getElementById('brightForm');
        const formData = new FormData(form);

        // Create a JSON object with the form data
        const data = {
            lamp1: parseInt(formData.get('lamp1')),
            lamp2: parseInt(formData.get('lamp2')),
            lamp3: parseInt(formData.get('lamp3')),
            lamp4: parseInt(formData.get('lamp4'))
        };

        // Send the data to the server (adjust URL to match your backend endpoint)
        fetch('/set_brightness', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Brightness set:', data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }