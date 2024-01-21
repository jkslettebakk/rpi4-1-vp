import glob
import time
import requests
import json
from datetime import datetime

API_URL = "https://SmartHouseAPI.slettebakk.com/api/TemperatureSensors-tmp"

ds18b20temperatureValues = {
    "28-0516938152ff" : "sensorTankTemp",
    "28-02189245921a" : "sensorVpTurTemp",
    "28-021892457738" : "sensorVpReturTemp",
    "28-0516938e3cff" : "sensorGulvTurTankTemp",
    "28-0209924508c6" : "sensorGulvReturTankTemp",
}

def find_ds18b20_sensors():
    return glob.glob("/sys/bus/w1/devices/28-*")

def read_temperature(sensor_path):
    try:
        with open(sensor_path + "/w1_slave", "r") as sensor_file:
            lines = sensor_file.readlines()
            temperature_str = lines[1].split(" ")[9]
            temperature = float(temperature_str[2:]) / 1000.0
            return temperature
    except Exception as e:
        print(f"Error reading temperature from {sensor_path}: {e}")
        return None

def read_temperatures(sensor_paths):
    try:
        temperatures = { }
        temperatures["sensorTankTimeStamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        for sensor_path in sensor_paths:
            sensor_id = sensor_path.split("/")[-1]
            temperature = read_temperature(sensor_path)
            print("Temperature = ", temperature)

            if temperature is not None:
                temperatures[ds18b20temperatureValues[sensor_id]] = temperature

        return temperatures
    except Exception as e:
        print(f"Error reading temperatures: {e}")
        return None

def send_data_to_api(data):
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, data=json.dumps(data), headers=headers)

        if response.status_code == 200:
                print("Data sent successfully.")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending data to API: {e}")

if __name__ == "__main__":
    try:
        while True:
            sensor_paths = find_ds18b20_sensors()
            temperatures = read_temperatures(sensor_paths)
            print(temperatures)

            if temperatures is not None:
                # Print the temperatures
                print(json.dumps(temperatures, indent=2))

                # Send data to the API
                send_data_to_api(temperatures)

            time.sleep(5)  # Adjust the delay as needed

    except KeyboardInterrupt:
        print("Program terminated by user.")
