import glob
import time

def find_ds18b20_sensors():
    # Use glob to find all DS18B20 sensor paths
    return glob.glob("/sys/bus/w1/devices/28-*")

def read_temperature(sensor_path):
    try:
        # Read temperature from the sensor file
        with open(sensor_path + "/w1_slave", "r") as sensor_file:
            lines = sensor_file.readlines()
            # Extract temperature from the second line
            temperature_str = lines[1].split(" ")[9]
            temperature = float(temperature_str[2:]) / 1000.0
            return temperature
    except Exception as e:
        print(f"Error reading temperature from {sensor_path}: {e}")
        return None

def read_temperatures(loopNr, sensor_paths):
    try:
        print(f"Reading {loopNr} results:")
        for sensor_path in sensor_paths:
            # Extract the sensor ID from the path
            sensor_id = sensor_path.split("/")[-1]
            temperature = read_temperature(sensor_path)

            if temperature is not None:
                # Print the temperature
                print(f"Sensor {sensor_id} Temperature: {temperature:.2f} °C")

    except Exception as e:
        print(f"Error reading temperatures: {e}")

if __name__ == "__main__":
    try:
        # Find all DS18B20 sensors
        sensor_paths = find_ds18b20_sensors()
        i = 0

        # Continue reading temperatures
        while True:
            i += 1; read_temperatures(i, sensor_paths)
            time.sleep(5)  # Adjust the delay as needed

    except KeyboardInterrupt:
        print("Program terminated by user.")
