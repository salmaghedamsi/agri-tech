#!/usr/bin/env python3
"""
IoT Sensor Data Simulator
Sends fake sensor data to test the IoT monitoring system
"""
import requests
import json
import random
import time
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:5000"
DEVICE_MAC = "AA:BB:CC:DD:EE:FF"

def simulate_sensor_data():
    """Generate realistic sensor data"""
    
    # Base values that fluctuate realistically
    base_temp = 25.0  # °C
    base_humidity = 60.0  # %
    base_soil = 1800  # sensor units
    
    # Add some realistic variation
    temp_variation = random.uniform(-3, 7)
    humidity_variation = random.uniform(-10, 15)
    soil_variation = random.uniform(-200, 400)
    
    # Time-based patterns (warmer during day, etc.)
    hour = datetime.now().hour
    if 6 <= hour <= 18:  # Daytime
        temp_variation += 3
        humidity_variation -= 5
    else:  # Nighttime
        temp_variation -= 2
        humidity_variation += 8
    
    return {
        'mac_address': DEVICE_MAC,
        'temp': round(base_temp + temp_variation, 1),
        'humidity': round(base_humidity + humidity_variation, 1),
        'soil': int(base_soil + soil_variation)
    }

def send_data_to_server(data):
    """Send sensor data to the IoT API"""
    try:
        response = requests.post(
            f"{SERVER_URL}/iot/api/data",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✓ Data sent successfully: {data}")
            return True
        else:
            print(f"✗ Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error: {e}")
        return False

def main():
    """Main simulation loop"""
    print("🌱 IoT Sensor Data Simulator")
    print("=" * 40)
    print(f"Target Server: {SERVER_URL}")
    print(f"Device MAC: {DEVICE_MAC}")
    print("=" * 40)
    print("Press Ctrl+C to stop")
    print()
    
    try:
        while True:
            # Generate and send sensor data
            sensor_data = simulate_sensor_data()
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"[{timestamp}] Sending data...")
            success = send_data_to_server(sensor_data)
            
            if success:
                print(f"    Temperature: {sensor_data['temp']}°C")
                print(f"    Humidity: {sensor_data['humidity']}%")
                print(f"    Soil Moisture: {sensor_data['soil']} units")
            
            print("-" * 30)
            
            # Wait before next reading (simulate sensor interval)
            time.sleep(30)  # Send data every 30 seconds
            
    except KeyboardInterrupt:
        print("\n👋 Simulator stopped by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()