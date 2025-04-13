#!/usr/bin/env python3
"""
Mobile GPS Tracker Client App
A simple Python app that can run on a mobile device (using a service like QPython)
to send GPS coordinates to the tracking server.
"""

import requests
import time
import json
import os
from datetime import datetime
import logging
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='gps_tracker_client.log',
    filemode='a'
)

# Default config
DEFAULT_CONFIG = {
    "server_url": "http://your-server-url.com",
    "device_id": "",
    "api_key": "",
    "update_interval": 30,  # seconds
    "min_distance": 10,  # meters
    "battery_monitor": True
}

# File paths
CONFIG_FILE = "gps_tracker_config.json"
LAST_LOCATION_FILE = "last_location.json"


def load_config():
    """Load configuration from file or create default if not exists"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            # Add any missing keys from default config
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
        else:
            # Create default config
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG


def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving config: {e}")


def load_last_location():
    """Load last recorded location"""
    try:
        if os.path.exists(LAST_LOCATION_FILE):
            with open(LAST_LOCATION_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading last location: {e}")
    return None


def save_last_location(location):
    """Save last recorded location"""
    try:
        with open(LAST_LOCATION_FILE, 'w') as f:
            json.dump(location, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving last location: {e}")


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters (simplified)"""
    from math import sin, cos, sqrt, atan2, radians

    # Approximate radius of earth in meters
    R = 6371000.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


def get_location():
    """
    Get current GPS location
    This is a stub function - in real usage, you would integrate with
    your platform's location services (Android, iOS, etc.)
    """
    try:
        # STUB: In real implementation, this would use device APIs
        # For Android, you might use QPython's Android API or a service like Termux API
        # For testing, you can use a random location near a base point

        import random

        # Base location (replace with actual coordinates for testing)
        base_lat = 40.7128  # NYC
        base_lon = -74.0060

        # Add small random offset (within ~100 meters)
        offset = 0.001  # ~100 meters
        lat = base_lat + random.uniform(-offset, offset)
        lon = base_lon + random.uniform(-offset, offset)

        return {
            "latitude": lat,
            "longitude": lon,
            "accuracy": random.uniform(5, 20),
            "altitude": random.uniform(0, 50),
            "speed": random.uniform(0, 10),  # m/s
            "heading": random.uniform(0, 359),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logging.error(f"Error getting location: {e}")
        return None


def get_battery_level():
    """
    Get device battery level
    This is a stub function - in real usage, you would integrate with
    your platform's battery monitoring services
    """
    try:
        # STUB: In real implementation, this would use device APIs
        import random
        return random.uniform(20, 100)
    except Exception as e:
        logging.error(f"Error getting battery level: {e}")
        return None


def send_location_update(config, location):
    """Send location update to server"""
    try:
        # Add required authentication fields
        location['device_id'] = config['device_id']
        location['api_key'] = config['api_key']

        # Add battery level if enabled
        if config['battery_monitor']:
            location['battery'] = get_battery_level()

        # Send data to server
        url = f"{config['server_url']}/api/update-location"
        response = requests.post(
            url,
            json=location,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            logging.info(f"Location update sent successfully: {location['latitude']}, {location['longitude']}")
            return True
        else:
            logging.error(f"Error sending location update: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error sending location update: {e}")
        return False


def should_update_location(config, current_location, last_location):
    """Determine if we should send an update based on distance and time"""
    if last_location is None:
        return True

    # Calculate time since last update
    last_time = datetime.fromisoformat(last_location['timestamp'])
    current_time = datetime.fromisoformat(current_location['timestamp'])
    time_diff = (current_time - last_time).total_seconds()

    # If it's been longer than the update interval, send update
    if time_diff >= config['update_interval']:
        # Calculate distance moved
        distance = calculate_distance(
            last_location['latitude'], last_location['longitude'],
            current_location['latitude'], current_location['longitude']
        )

        # Only update if we've moved minimum distance
        return distance >= config['min_distance']

    return False


def register_device(config):
    """Register this device with the tracking server"""
    try:
        # Only try to register if we don't have a device ID
        if config['device_id']:
            return True

        device_info = {
            "model": os.environ.get('DEVICE_MODEL', 'Unknown'),
            "name": os.environ.get('DEVICE_NAME', f"Device-{int(time.time())}"),
            "platform": os.environ.get('DEVICE_PLATFORM', 'Unknown'),
            "version": os.environ.get('DEVICE_VERSION', '1.0')
        }

        url = f"{config['server_url']}/api/register-device"
        response = requests.post(
            url,
            json=device_info,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            result = response.json()
            config['device_id'] = result.get('device_id', '')
            config['api_key'] = result.get('api_key', '')
            save_config(config)
            logging.info(f"Device registered successfully with ID: {config['device_id']}")
            return True
        else:
            logging.error(f"Error registering device: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error registering device: {e}")
        return False


def main():
    """Main function that runs the client app"""
    parser = argparse.ArgumentParser(description='GPS Tracker Client')
    parser.add_argument('--setup', action='store_true', help='Run setup configuration')
    parser.add_argument('--server', type=str, help='Server URL')
    parser.add_argument('--interval', type=int, help='Update interval in seconds')
    parser.add_argument('--min-distance', type=int, help='Minimum distance for updates in meters')
    parser.add_argument('--test', action='store_true', help='Run in test mode with simulated locations')
    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Update config from command line args
    if args.server:
        config['server_url'] = args.server
    if args.interval:
        config['update_interval'] = args.interval
    if args.min_distance:
        config['min_distance'] = args.min_distance

    # Save updated config
    save_config(config)

    # Run setup if requested
    if args.setup:
        server_url = input(f"Enter server URL [{config['server_url']}]: ") or config['server_url']
        update_interval = input(f"Enter update interval in seconds [{config['update_interval']}]: ") or config[
            'update_interval']
        min_distance = input(f"Enter minimum distance for updates in meters [{config['min_distance']}]: ") or config[
            'min_distance']

        config['server_url'] = server_url
        config['update_interval'] = int(update_interval)
        config['min_distance'] = int(min_distance)

        save_config(config)
        print("Configuration saved!")
        return

    # Ensure device is registered
    if not register_device(config):
        print("Failed to register device with the tracking server. Exiting.")
        return

    print(f"Starting GPS tracker client. Sending updates every {config['update_interval']} seconds.")
    print(f"Updates will only be sent if device moves at least {config['min_distance']} meters.")
    print(f"Press Ctrl+C to stop.")

    try:
        while True:
            # Get current location
            current_location = get_location()
            if current_location is None:
                logging.warning("Failed to get location. Retrying...")
                time.sleep(5)
                continue

            # Load last location
            last_location = load_last_location()

            # Check if we should send an update
            if should_update_location(config, current_location, last_location):
                if send_location_update(config, current_location):
                    # Save this location as the last location
                    save_last_location(current_location)

            # Sleep until next update
            time.sleep(config['update_interval'])
    except KeyboardInterrupt:
        print("GPS tracker client stopped.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()