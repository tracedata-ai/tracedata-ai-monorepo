import time
import json
import random

def generate_telemetry(vehicle_id):
    return {
        "vehicle_id": vehicle_id,
        "timestamp": time.time(),
        "gps": {
            "lat": 1.3521 + random.uniform(-0.01, 0.01),
            "lng": 103.8198 + random.uniform(-0.01, 0.01)
        },
        "tire_pressure": [random.uniform(30, 35) for _ in range(4)],
        "fuel_level": random.uniform(10, 100),
        "speed": random.uniform(0, 80)
    }

if __name__ == "__main__":
    vehicle_id = "CAR-001"
    print(f"Starting telemetry for {vehicle_id}...")
    try:
        while True:
            data = generate_telemetry(vehicle_id)
            print(f"Publishing: {json.dumps(data)}")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Simulation stopped.")
