#! /usr/bin/env python

import os
import glob
import time
import requests
import datetime
import sys
from numpy import *

# vp.py version 1, last stable
# 2019-05-13
# (r) slettebakk.com

# Typical reading from several sensors
# 73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
# 73 01 4b 46 7f ff 0d 10 41 t=34000
#
# t in 1000 degrees centigrade -> 34000 = 34 degrees
#
Start_Time = datetime.datetime.now()
time_sleep = 10.0 # 10 seconds between every sensor poll
reading_numbers = 1 # Counter for total number of sensor/data polls
url = 'https://vp.slettebakk.com/api/TemperatureVP' # se also POST json structure below
logInformation = False # set to True if you want extended logging
# sample JSON structure for POST back to REST API and further to database
#[
#  {
#    "temperatureId": "3a03badf-fe62-4276-8ee3-31f9e075b21d",
#    "sensorTankTimeStamp": "2019-05-13T20:38:35",
#    "sensorTankTemp": 38.00,
#    "sensorVpTurTemp": 46.00,
#    "sensorVpReturTemp": 39.00,
#    "sensorGulvTurTankTemp": 37.00,
#    "sensorGulvReturTankTemp": 31.00,
#    "sensorACVannReservoar": 220.00
#  }
#]
#
sensorNames = ["sensorTankTimeStamp",
               "sensorTankTemp",
               "sensorVpTurTemp",
               "sensorVpReturTemp",
               "sensorGulvTurTankTemp",
               "sensorGulvReturTankTemp",
               "sensorACVannReservoar" ]
# dependensies
# REST API using POST and GET
#
# first, check if REST point is up running
# you decide if this test is important.  Since you use REST the total valuechain should be robust enough this handle exception
try:
    HTTPSResult = requests.get(url) # This command will take considerable time when you have a lot of data
except requests.exceptions.Timeout:
    # Maybe set up for a retry, or continue in a retry loop
    print( 'Timeout on url: \x1b[6;30;42m', url, '\x1b[0m')
except requests.exceptions.TooManyRedirects:
    # Tell the user their URL was bad and try a different one
    print( 'To many redirects on url: \x1b[6;30;42m', url, '\x1b[0m')
except requests.exceptions.RequestException as e:
    # catastrophic error. bail.
    print('Catastrophical error occured in : \x1b[6;31;42m', url, '\x1b[0m\n')
    print( e )
    exit()


# OK, HTTPS call is ok, but is it 200
if ( logInformation):
    print('Read from the API\n', HTTPSResult.text)

if HTTPSResult.status_code == 200:
    print('Sucsessfull lookup in ', url, ' with HTTPS result = ', HTTPSResult.status_code)
else:
    print( '\nError in contacting REST CRUD url.\nREST/CRUD url error is: ', HTTPSResult.status_code, '\nStopping further prosessing\n')
    exit()



# Get number of sensors. I need to find a mapping method to right ds18b26
sensors = len(glob.glob('/sys/bus/w1/devices/28-*/w1_slave'))

# if sensor is 0 or less, gracefully stop further processing
if sensors <= 0:
   print('\nIt seems to be no sensors connected.\n\nNumber of temperature sensors is: ', sensors, '\nGracfully stopping further prosessing\n')
   exit()

# Initiate data tables for temperature sensors
# array for storing max data (dont know how to use this yet)
max_temp_sensor = []
for i in range(sensors):
   # print('i=', i)
   max_temp_sensor.append(-273)
# array for min temperatures (dont know how this will be used yet)
min_temp_sensor = []
for i in range(sensors):
   # print( 'i=', i)
   min_temp_sensor.append(10000)

old_temp_sensor = []
for i in range(sensors):
   # print( 'i=', i)
   old_temp_sensor.append(-273)

# array for real data
reading_values = []
for i in range(sensors):
   # print( 'i=', i)
   reading_values.append(' Text will be filled in')

json = ""
oldVpTurTemp = -273.000  # used to evaluate the delta temperature change
oldTankTemp = -273.000
diffTemperature = 0.01  # 1% temperature change
writeTankTemp = False
writeVpTemp = False

# Ok, all preparation done, looping forever....
while True:

   reading_sensor = 0
   timePolled = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
   json =   '{\n' + '\t\"' + sensorNames[reading_sensor] + '\": "' + timePolled + '\"'
   
   print('\nReading number ', reading_numbers)
   
   for sensor in glob.glob("/sys/bus/w1/devices/28-*/w1_slave"):
      id = sensor.split("/")[5]
      if ( logInformation):
          print( 'Checking sensor = ', sensor, ' id =', id)

      try:
         f = open(sensor, "r")
         data = f.read()
         f.close()
         if ( logInformation ):
             print( 'Data lest = ', data, ' fra file= ', f)
         if "YES" in data:
            (discard, sep, reading) = data.partition(' t=')
            temperature = float(reading) / 1000.0

            if temperature == 0 : temperature = 0.0+sys.float_info.epsilon # temperature cant be 0.0 since used in divitions

            # Looging to screen
            reading_values[reading_sensor] = 'Sensor: {0:1d} ({1:}), Sensor ID: {2:s} Temperature: {3:.1f} and diff {4:.1f}'.format(reading_sensor,
                                                sensorNames[reading_sensor + 1],
                                                id,
                                                temperature,
                                                (old_temp_sensor[reading_sensor]-temperature))

            # storing data for temporary use
            old_temp_sensor[reading_sensor] = temperature
            max_temp_sensor[reading_sensor] = max(max_temp_sensor[reading_sensor],temperature)
            if ( logInformation ):
                print( 'setting max of sensor ', reading_sensor, ' with max=', max_temp_sensor[reading_sensor], ' and temp = ', temperature)
            min_temp_sensor[reading_sensor] = min(min_temp_sensor[reading_sensor],temperature)
            if ( logInformation ):
                print( 'setting min of sensor ', reading_sensor, ' with min=', min_temp_sensor[reading_sensor], ' and temp = ', temperature)

            json = json + ',\n\t\"{0}\": \"{1}\"'.format(sensorNames[reading_sensor + 1],temperature)

            if (sensorNames[reading_sensor + 1] == 'sensorTankTemp' ):
                if ( logInformation ):
                     print("Testing delta temp sensor: ", sensorNames[reading_sensor + 1])
                diffTankTemp = abs((oldTankTemp - temperature) / temperature)
                if ( diffTankTemp > diffTemperature ): 
                     writeTankTemp = True
                     oldTankTemp = temperature
            if (sensorNames[reading_sensor + 1] == 'sensorVpTurTemp' ):
                if ( logInformation ):
                     print("Testing delta temp sensor: ", sensorNames[reading_sensor + 1])
                diffVpTemp = abs((oldVpTurTemp - temperature) / temperature)
                if ( diffVpTemp  > diffTemperature ):
                     writeVpTemp = True
                     oldVpTurTemp = temperature
            print( reading_values[reading_sensor] )
            reading_sensor = reading_sensor + 1
         else:
            print( 'Error in prosessing sensors:\n', e)
            # Could i restart?            
            exit()
      except:
          print( 'Error in try: sensor data extract:\n', e)
          # Could i restart?
          exit()

          for i in range(sensors):
            print('i=',i, 'values=', reading_values[i], ' High:', max_temp_sensor[i] , ' and low:', min_temp_sensor[i])

   Time_delta = datetime.datetime.now() - Start_Time
   print('Sleeping ', time_sleep, 'sec.\nHas been running for ;', Time_delta.days, ' day(s), ', Time_delta.seconds/3600, ' hr(s), ', (Time_delta.seconds % 3600)/60, ' min and ', Time_delta.seconds % 60, 'sec.')
   json = json + '\n}'

   # print('\nwriteTankTemp=', writeTankTemp, ' og writeVpTemp=', writeVpTemp)

   if ( writeTankTemp or writeVpTemp ):
        print('json:\n', json)
        writeVpTemp = False
        writeTankTemp = False

        try:
            HTTPSResult = requests.post(url, data=json, headers={'Content-Type':'application/json'})
            print('HTTPSResult POST result = ', HTTPSResult.status_code)
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            print('Timeout on POST to url: \x1b[6;30;42m', url, '\x1b[0m')
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print('To many redirects on url: \x1b[6;30;42m', url, '\x1b[0m')
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print('catastrophic error. bail on url: \x1b[6;30;41m', url, '\x1b[0m')
            print(e)
            error = '\nSom error occured at {0} and the content is:\n {1}\n'.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),e)
            print(error)
            f = open('vp.log', 'a')
            f.write(error)
            f.close()
            # exit()
   else:
            print('\nSkipped storing {0: 0.2f}C'.format(temperature) + ' at ' + timePolled + ' (' + str(diffTemperature*100) + '% compared to {0: 0.2f}C'.format(oldTankTemp) + ' (diff tank {0: 0.2f}'.format(diffTankTemp) + ' (diff VP {0: 0.2f}'.format(diffVpTemp) + ')). Polling every {}s.'.format(time_sleep))
 

   time.sleep(time_sleep)
   reading_numbers = reading_numbers + 1
