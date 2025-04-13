from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# HTML template with auto-location code
"""HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
  <title>Auto GPS Tracker</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
  <h2>Getting your location...</h2>
  <p id="status">Please wait...</p>

  <script>
    window.onload = function () {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(sendPosition, showError);
      } else {
        document.getElementById("status").innerText = "Geolocation not supported.";
      }
    };

    function sendPosition(position) {
      const data = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
      };

      fetch("/location", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      })
      .then(response => response.text())
      .then(result => {
        document.getElementById("status").innerText = result;
      });
    }

    function showError(error) {
      document.getElementById("status").innerText = "Error getting location.";
    }
  </script>
</body>
</html>
'''"""

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
  <title>Free GPS Map Tracker</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.3/dist/leaflet.css" />

  <style>
    #map {
      height: 90vh;
      width: 100%;
    }
    body {
      margin: 0;
      font-family: sans-serif;
      text-align: center;
    }
  </style>
</head>
<body>

  <h2>📍 Your Live Location</h2>
  <div id="map">Loading map...</div>

  <!-- Leaflet JS -->
  <script src="https://unpkg.com/leaflet@1.9.3/dist/leaflet.js"></script>

  <script>
    function showMap(lat, lon) {
      const map = L.map('map').setView([lat, lon], 15);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      L.marker([lat, lon]).addTo(map)
        .bindPopup("You are here")
        .openPopup();
    }

    function showError() {
      document.getElementById("map").innerText = "Failed to get location.";
    }

    window.onload = function () {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
          const lat = pos.coords.latitude;
          const lon = pos.coords.longitude;

          showMap(lat, lon);

          // Optional: Send to Flask backend
          fetch("/location", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ latitude: lat, longitude: lon })
          });

        }, showError);
      } else {
        showError();
      }
    };
  </script>

</body>
</html>
'''


@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/location', methods=['POST'])
def location():
    data = request.json
    lat = data.get('latitude')
    lon = data.get('longitude')
    print(f"Received coordinates: Latitude = {lat}, Longitude = {lon}")
    return f"Location received: {lat}, {lon}"

if __name__ == '__main__':
    app.run(debug=True)
