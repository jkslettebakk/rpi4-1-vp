import time
import requests
import glob
import os

# Function to read temperature from a single DS18B20 sensor
def read_temp(sensor_id):
    try:
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + sensor_id)[0]
        device_file = device_folder + '/w1_slave'
        with open(device_file, 'r') as f:
            lines = f.readlines()
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = f.readlines()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
    except Exception as e:
        print(f"Error reading sensor {sensor_id}: {e}")
        return None

# Main loop
def main():
    sensor_ids = ['28-0209924508c6', '28-021892457738', '28-02189245921a', '28-0516938152ff', '28-0516938e3cff'] # Replace with your actual sensor IDs

    while True:
        readings = []
        response = []
        for sensor_id in sensor_ids:
            temp = read_temp(sensor_id)
            if temp is not None:
                readings.append({'sensor_id': sensor_id, 'temperature': temp})

        # Post readings to API
        if readings:
            try:
                tmpJson=json=readings
                # response = requests.post('https://SmartHouseAPI.slettebakk.com/api/TemperatureSensors',
                #                          json=readings)
                response.append({'text' : 'OK'})
                print(f"Data posted successfully: {response[0].text}")
            except requests.exceptions.RequestException as e:
                print(f"Failed to post data: {e}")
                print(f"Json result = {tmpJson}")
        
        time.sleep(10) # Sleep for 10 seconds

if __name__ == "__main__":
    main()
