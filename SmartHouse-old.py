#! /usr/bin/env python
#
import os
import json
import glob
import time
import requests
import datetime
import sys, subprocess

import numpy
#
# SmartHouse.py
# version 1.1
# 2020-01-19T18:08
# (r) slettebakk.com
#
# Typical reading from several sensors
# 73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
# 73 01 4b 46 7f ff 0d 10 41 t=34000
#
# t in 1000 degrees centigrade :) 34000 = 34 degrees
#
Start_Time = datetime.datetime.now()
time_sleep = 10.0  # 10 seconds between every sensor poll
reading_numbers = 1  # Counter for total number of sensor/data polls
# se also POST json structure below
NetAtmoPy = "/home/pi/Documents/py4netatmo.py"
SmartHousePy = "/home/pi/Documents/SmartHouse.py"
SmartHouseApiUrl = 'https://SmartHouseAPI.slettebakk.com/api/TemperatureSensors'
logInformation = False  # set to True if you want extended logging
resultJsonFile = "/home/pi/Documents/netAtmoResult.json"
#
''' sample JSON structure for POST back to REST API and further to database
[
    {
        "temperatureId": "2d7f1009-0851-4a76-1ce8-08d7857799e6",
        "sensorTankTimeStamp": "2019-12-20T20:44:18",
        "sensorTankTemp": 39.03,
        "sensorVpTurTemp": 42.10,
        "sensorVpReturTemp": 37.10,
        "sensorGulvReturTankTemp": 33.10,
        "sensorGulvTurTankTemp": 36.80,
        "indorTemperature": 22.90,
        "outdorTemperature": -5.00
    }
]
'''
sensorNames = ["sensorTankTimeStamp",
               "sensorTankTemp",
               "sensorVpTurTemp",
               "sensorVpReturTemp",
               "sensorGulvTurTankTemp",
               "sensorGulvReturTankTemp",
               "sensorACVannReservoar"]
# Indor and Outdor sensor data will come from NetAtmo json data structures like this:
'''
{
    "devices": [
        {
            "_id": "70:ee:50:3c:f4:20",
            "station_name": "Ospestien51",
            "date_setup": 1556983885,
            "last_setup": 1556983885,
            "type": "NAMain",
            "last_status_store": 1577090657,
            "module_name": "Ospestien 51 inne",
            "firmware": 140,
            "last_upgrade": 1556983886,
            "wifi_status": 44,
            "reachable": true,
            "co2_calibrating": false,
            "data_type": [
                "Temperature",
                "CO2",
                "Humidity",
                "Noise",
                "Pressure"
            ],
            "place": {
                "altitude": 115,
                "city": "Asker",
                "country": "NO",
                "timezone": "Europe/Oslo",
                "location": [
                    10.4438908,
                    59.831686499999996
                ]
            },
'''
# dependensies
# REST API using HEAD and POST
#
# first, check if REST point is up running with head
# you decide if this test is important.  Since you use REST the total valuechain should be robust enough this handle exception
try:
    # This command is looking for the header information...
    HTTPSResult = requests.head(SmartHouseApiUrl)
except requests.exceptions.Timeout:
    # Maybe set up for a retry, or continue in a retry loop
    print('Timeout on url: \x1b[6;30;42m', SmartHouseApiUrl, '\x1b[0m')
except requests.exceptions.TooManyRedirects:
    # Tell the user their URL was bad and try a different one
    print('To many redirects on url: \x1b[6;30;42m', SmartHouseApiUrl, '\x1b[0m')
except requests.exceptions.RequestException as e:
    # catastrophic error. bail.
    print('Catastrophical error occured in : \x1b[6;31;42m', SmartHouseApiUrl, '\x1b[0m\n')
    print(e)
    exit()


# OK, HTTPS call is ok, but is it 200
if (logInformation):
    print("Read from the API\n{}".format(HTTPSResult.text))

if (HTTPSResult.status_code == 200):
    print("Successfull lookup in {} \nHTTPS result : {} \nHTTP head :\n{}".format(
        SmartHouseApiUrl, HTTPSResult.status_code, HTTPSResult.headers))
else:
    print("\nError in contacting REST CRUD url.\nREST/CRUD url error is: {}\nStopping further prosessing\n".format(
        HTTPSResult.status_code))
    exit()

# Get number of sensors. I need to find a mapping method to right ds18b26
sensors = len(glob.glob('/sys/bus/w1/devices/28-*/w1_slave'))

# if sensor is 0 or less, gracefully stop further processing
if (sensors <= 0):
    print('\nIt seems to be no sensors connected.\n\nNumber of temperature sensors is: {}\nGracfully stopping further prosessing\n'.format(
        sensors))
    exit()

# Initiate data tables for temperature sensors
# array for storing min/max data (dont know how to use this yet)
max_temp_sensor = []
min_temp_sensor = []
# array for old temperature meassurements
old_temp_sensor = []
diff_temp_sensor = []
# array for real data
reading_values = []
#
for i in range(sensors):
    # print('i=', i)
    max_temp_sensor.append(-273)  # Initiate with extreeme values
    min_temp_sensor.append(10000)
    old_temp_sensor.append(-273)
    reading_values.append(' Text will be filled in')
    diff_temp_sensor.append(10000)

if (logInformation):
    print('max_temp_sensor array:{}\n'.format(
        max_temp_sensor))

jsonString = ""
deltaTemperature = 0.01  # When we have 1% temperature change, save data
writeJsonDataToDatabase = False
inDoorTemperature = -273
outDoorTemperature = -273

# Ok, all preparation done, looping forever....
while True:

    reading_sensor = 0
    timePolled = datetime.datetime.fromtimestamp(
        time.time()).strftime('%Y-%m-%dT%H:%M:%S.%f')
    jsonString = '{\n' + '\t\"' + \
        sensorNames[reading_sensor] + '\": "' + timePolled + '\"'

    print('\nReading number ', reading_numbers)

# looping for all sensors every 10 seconds
    for sensor in glob.glob("/sys/bus/w1/devices/28-*/w1_slave"):
        id = sensor.split("/")[5]
        if (logInformation):
            print('Checking sensor = ', sensor, ' id =', id)

        try:
            f = open(sensor, "r")
            data = f.read()
            f.close()
            if (logInformation):
                print('Data lest = ', data, ' fra file= ', f)
            if "YES" in data:
                (discard, sep, reading) = data.partition(' t=')
                temperature = float(reading) / 1000.0

                if temperature == 0:
                    # temperature cant be 0.0 since used in divitions
                    temperature = 0.0+sys.float_info.epsilon

                # Looging to screen
                reading_values[reading_sensor] = \
                    'Sensor: {0:1d} ({1:}), Sensor ID: {2:s} Temperature: {3:.1f} and diff {4:.1f} ({5:.1f}%))'.format(reading_sensor,
                                                                                                                       sensorNames[
                                                                                                                           reading_sensor + 1],
                                                                                                                       id,
                                                                                                                       temperature,
                                                                                                                       (old_temp_sensor[reading_sensor]-temperature),
                                                                                                                       abs(abs(old_temp_sensor[reading_sensor] - temperature) / temperature)*100)

                max_temp_sensor[reading_sensor] = max(
                    max_temp_sensor[reading_sensor], temperature)
                if (logInformation):
                    print('setting max of sensor ', reading_sensor, ' with max=',
                          max_temp_sensor[reading_sensor], ' and temp = ', temperature)
                min_temp_sensor[reading_sensor] = min(
                    min_temp_sensor[reading_sensor], temperature)
                if (logInformation):
                    print('setting min of sensor ', reading_sensor, ' with min=',
                          min_temp_sensor[reading_sensor], ' and temp = ', temperature)

                jsonString = jsonString + \
                    ',\n\t\"{0}\": {1}'.format(
                        sensorNames[reading_sensor + 1], temperature)

                if (logInformation):
                    print('Sensor: {} is {}'.format(
                        reading_sensor, sensorNames[reading_sensor + 1]))
                # Calculate differences
                diff_temp_sensor[reading_sensor] = abs(
                    abs(old_temp_sensor[reading_sensor] - temperature) / temperature)
                if (diff_temp_sensor[reading_sensor] > deltaTemperature):
                    writeJsonDataToDatabase = True
                    old_temp_sensor[reading_sensor] = temperature

                print(reading_values[reading_sensor])
                reading_sensor = reading_sensor + 1
            else:
                print('Error in prosessing sensors:\n', e)
                # Could i restart?
                exit()
        except:
            print('Error in try: sensor data extract:\n', e)
            # Could i restart? I need to learn based upon crashes, but for now I use exit()
            exit()

    if (logInformation):
        for i in range(sensors):
            print('i=', i, 'values=', reading_values[i], ' High:',
                    max_temp_sensor[i], ' and low:', min_temp_sensor[i])
# ready to get netatmo data
    if (writeJsonDataToDatabase):
        # All sensors prosessed and ready to write sensor data... look for and add wheather data
        try:
            print("Before subprocess.check_output")
            wetherStreamData = subprocess.check_output(["python3", "py4netatmo.py"], universal_newlines=True)
            print("After subprocess.check_output")
        except wetherStreamData.exceptions as e:
            print('Error in python NetAtmo subprosess: {}. Error message = {}'.format(wetherStreamData,e))

        # remove \n (newline)
        wetherStreamData = wetherStreamData.rstrip()

        # change from ' to "
        wetherStreamData = wetherStreamData.replace("'",'"')

        # covert to proper json formatted string
        wetherStreamData = json.loads(wetherStreamData)

        # Reading last netAtmo data elements
        netatmoUtcTime = wetherStreamData["time_utc"]
        inDoorTemperature = wetherStreamData["inhouse"]
        outDoorTemperature = wetherStreamData["outdor"]


        print("Sucsessfully read netatmo indor ({}) and outdor ({}) temperature at {}.".format(inDoorTemperature, outDoorTemperature, netatmoUtcTime))
        print("Time now is {}".format(datetime.datetime.now()))

        jsonString = jsonString + \
            ',\n\t\"{0}\": {1}'.format(
                "indorTemperature", inDoorTemperature)
        jsonString = jsonString + \
            ',\n\t\"{0}\": {1}'.format(
                "outdorTemperature", outDoorTemperature)

        # Close prepared json string
        jsonString = jsonString + '\n}'
        print('jsonString to POST to API ({}) endpoint:\n{}'.format(SmartHouseApiUrl,jsonString))
        writeJsonDataToDatabase = False

        try:
            HTTPSResult = requests.post(SmartHouseApiUrl, data=jsonString, headers={'Content-Type':'application/json'})
            print('POST HTTPSResult={}\nURI to Location id={}'.format(HTTPSResult.status_code, HTTPSResult.headers["Location"]) )
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            print('Timeout on POST to url: \x1b[6;30;42m', SmartHouseApiUrl, '\x1b[0m')
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print('To many redirects on url: \x1b[6;30;42m', SmartHouseApiUrl, '\x1b[0m')
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print(
                'catastrophic error. bail on url: \x1b[6;30;41m', SmartHouseApiUrl, '\x1b[0m')
            print(e)
            error = '\nSom error occured at {0} and the content is:\n {1}\n'.format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), e)
            print(error)
            f = open('SmartHouse.log', 'a')
            f.write(error)
            f.close()
            # exit()
        except:
            print("Some unhadled exception ocured. requests.... not executed? Other error. Contune....")
    else:
            #print('\nSkipp storing {0: 0.2f}C'.format(temperature) + ' at ' + timePolled + ' (' + str(deltaTemperature*100) + '% compared to {0: 0.2f}C'.format(old_temp_sensor[reading_sensor]) + ' (diff tank {0: 0.2f}'.format(diffTankTemp) + ' (diff VP {0: 0.2f}'.format(diffVpTemp) + ')). Polling every {}s.'.format(time_sleep))
        print('Skipped storing datapoll number {}. Limited changes in sensor data from last reading'.format(reading_numbers))

    Time_delta = datetime.datetime.now() - Start_Time
    if ( logInformation): print('Time_delta = {}'.format(Time_delta))
    print('\nSleeping {0:.0f} sec.\nHas been running for ; {1:.0f} day(s), {2:.0f} hr(s), {3:.0f} min and {4:.0f}.{5:.0f} sec.'.format(
        time_sleep, Time_delta.days, int(Time_delta.seconds / 3600), int((Time_delta.seconds % 3600)/60), (Time_delta.seconds % 60), Time_delta.microseconds))

    time.sleep(time_sleep)
    reading_numbers = reading_numbers + 1
