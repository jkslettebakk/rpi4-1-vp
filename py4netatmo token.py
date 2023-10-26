#! /usr/bin/env python
#
#
import requests
import time
import datetime
import json
import getpass
import hashlib
import binascii
import os
#
#
# some global(?) variables...
#
debugLevel0 = True  # Data og Info
debugLevel1 = True  # Info/warnings
debugLevel2 = True  # Criticalwarning/error
debugLevel3 = True  # Security data, normally not to be displayed
netAtmoJsonData = True  # Set True if you want the NetAtmo data logged to file

# print("debugLevel0=",debugLevel0)

netAtmoRunningCatalogue = "/home/pi/Documents/vp/"
accountFile = netAtmoRunningCatalogue + 'account token.json'
tokenFileName = netAtmoRunningCatalogue + 'token.json'
resultJsonFile = netAtmoRunningCatalogue + "netAtmoResult.json"
netatmoStationData = netAtmoRunningCatalogue + 'netatmoStationData.json'
netAtmoTokenURL = 'https://api.netatmo.net/oauth2/token'
geStationDataURL = 'https://api.netatmo.net/api/getstationsdata'
global netAtmoAccoungJsonData
global netAtmoTokenJsonData
global netAtmoDeviceID
global netAtmoDeviceJsonData
global tokenData
global expiredTokenTime

tokenData = ''
netAtmoDeviceID = ''
expiredTokenTime = 0

#
# define some functions. Should i use classes?
#

def generateNetAtmoToken(tokenFileName, netAtmoTokenURL, netAtmoAccoungJsonData):
    if debugLevel1:
        print('Debug Level1:\nReady to generate NetAtmo token data before downloading weather data')
    # get data from NetAtmo
    payload = {'grant_type': 'refresh_token',
               'refresh_token': netAtmoAccoungJsonData['refresh_token'],
               'client_id': netAtmoAccoungJsonData['client_id'],
               'client_secret': netAtmoAccoungJsonData['client_secret'],
               'scope': ''}

    if debugLevel3:
        print('Debug Level3:\nPayload:\n{}'.format(payload))
    try:
        print('Start request response heading')
        # resp = requests.post(netAtmoTokenURL, payload)
        # print('Token status?:\n',resp)
        response = requests.post(netAtmoTokenURL, data=payload)
        print('After request response:',response)

        response.raise_for_status()
        print('After request response status:',response)
        netAtmoAccoungJsonData = response.json()
        print('After netAtmoAccoungJsonData:',netAtmoAccoungJsonData)
        access_token = netAtmoAccoungJsonData["access_token"]
        print('After access_token:',access_token)
        refresh_token = netAtmoAccoungJsonData["refresh_token"]
        print('After refresh_token:',refresh_token)
        scope = netAtmoAccoungJsonData["scope"]
        print('After scope:',scope)

        if debugLevel1:
            print('Debug level1:\n')
            print('Debug level1: Your access token is:', access_token)
            print('Debug level1: Your refresh token is:', refresh_token)
            print('Debug level1: Your scopes are:', scope)
    except requests.exceptions.HTTPError as error:
        print(error.response.status_code, error.response.text)
        # Cant continue with error/missing data from this point onwords
        exit(error)
    # All good, we have token data, now save it to the file...

    try:
        with open(tokenFileName, 'w', encoding='utf-8') as tokenDataWrite:
            json.dump(response.json(), tokenDataWrite, indent=4)
        tokenDataWrite.close()
    except Exception as e:
        if debugLevel1:
            print('Error writing token data with error:\n{}'.format(e))
        exit(e)

    if debugLevel1:
        print('Debug Level1:\nResponce result:\n{}'.format(response.json()))
    # generateNetAtmoToken done


def initNetAtmo(tokenData, netAtmoDeviceID):
    # 1) Check if we have a valid token, if not
    #   1.5) Get a new valid token
    # 2) Check if token is expired, if not
    #   2.5 renew token
    # 3) return ready to get data
    #
    # One files is needed (account.json), one file will be created if it does not exist (token.json)
    # read NetAtmo account data
    try:
        with open(accountFile, 'r') as accountData:
            data = accountData.read()
        accountData.close()
        print('initNetAtmo data loaded:\n', data)
    except Exception as e:
        print('Fatal error')
        print('You need to provide NetAtmo logon account data to get passed this point.')
        print('The {} file typically contain:\n'.format(accountFile))
        tmp = """{
            "client_id"    : "5ceefcc7affea06260773347",
            "client_secret": "ocSSJKhh8byLGuQmt0vad714YbK",
            "refresh_token": "5ccdae726b5cc20a008b71e9|3f1d3d96cb43610f31d50e746e085063",
            "device_id"    : "71:ef:30:4a:d5:19"
            }"""
        tmp_parsed = json.loads(tmp)
        print(json.dumps(tmp_parsed, indent=4))
        exit(e)

    # OK, lets parce file data
    netAtmoAccoungJsonData = json.loads(data)
    netAtmoDeviceID = netAtmoAccoungJsonData['device_id']
    refreshToken = netAtmoAccoungJsonData['refresh_token']
    if ( debugLevel1 ):
        print('initNetAtmo() - netAtmoDeviceID=', netAtmoDeviceID)
        print('initNetAtmo() - refreshToken= ', refreshToken)
    if debugLevel3:
        print('Debug level3:\nAccount binary data:\n{}\n'.format(data))
    if debugLevel2:
        print('Debug level2:\ndevice_id:{}\nclient_secret:{}\nrefresh_token:{}\ndevice_id:{}\n'.format(netAtmoDeviceID,netAtmoAccoungJsonData['client_secret'], netAtmoAccoungJsonData['refresh_token'], netAtmoAccoungJsonData['device_id']))
    if debugLevel1:
        print('Debug level1:\nNetAtmo initialization done')

    # Now, token data is loaded from 
    try:
        with open(tokenFileName, 'r') as readTokenDataFile:
            tokenData = readTokenDataFile.read()
        readTokenDataFile.close()
        print('Token Data read:\n',tokenData)
        if tokenData is None:
            raise Exception('The token.json file is empty')
    except FileNotFoundError as fnf_error:
        # Token file does not exists
        if debugLevel1:
            print('Debug level1:\nWarning.\n{}.Token file will be generated. Calling "generateNetAtmoToken"'.format(fnf_error))
        # need to generate token data
        generateNetAtmoToken(tokenFileName, netAtmoTokenURL,
                             netAtmoAccoungJsonData)
        print('After "generateNetAtmoToken"')
        try:
            with open(tokenFileName, 'r') as readTokenDataFile:
                tokenData = readTokenDataFile.read()
            readTokenDataFile.close()
            print('Token data read:\n',tokenData)
        except Exception as e:
            # Token file does not exists
            if debugLevel1:
                print(
                    'Debug level1:\nToken file does not exist. {}. Problems generating data from your NetAtmo account.'.format(e))
            print('ERROR:\nI need to stop futher processing.')
            exit(e)

    # Token data catching finish?
    if debugLevel3:
        print('Debug level3:\nToken binary data:\n{}\n'.format(tokenData))
    if ( debugLevel1):
        print('returning initNetAtmo() \ntokenData:{}\nnetAtmoDeviceID{}:'.format(
            tokenData, netAtmoDeviceID))
    return (tokenData, netAtmoDeviceID)
    # End initNetAtmo()


def getNetAtmoData(tokenData, netAtmoDeviceID):
    # Now, requesting data should be safe.....
    # first check if token data/key's is stil valid/has not expired
    print('Enter getNetAtmoData')
    currentTime = time.time()
    tokenDataTimeModified = os.stat(tokenFileName).st_mtime
    expireTime = tokenDataTimeModified + json.loads(tokenData)["expire_in"]
    if debugLevel1:
        print('Debud level1:\nTokenData:', tokenData)
        print('Expires in:', json.loads(tokenData)["expires_in"])
        print('Expires time (in seconds from epoc):', expireTime)
        print('Expires time:', time.ctime(expireTime))
        print('Current time:', time.ctime(currentTime))
    if (currentTime >= (expireTime - 500)): # minus 5 sec. for prosessing
        print('Need to renew token file. It expired {} minutes ago.'.format(
            (int(currentTime-expireTime)/60)))
        # delete tokenDataFile
        os.remove(tokenFileName)
        # then initiate data
        initNetAtmo(tokenData, netAtmoDeviceID)
    else:
        print('Token file ok. It will expire in {} minutes.'.format(
            int((expireTime-(currentTime-500))/60)))
    # Then we are ready to refrsh data from NetAtmo database

    if (debugLevel1):
        print('getNetatmoData() - netAtmoDeviceID:\n', netAtmoDeviceID, 'access token:\n',json.loads(tokenData)['access_token'])

    params = {
        'access_token': json.loads(tokenData)['access_token'],
        'device_id': netAtmoDeviceID
    }
    try:
        print('Request data from Netatmo')
        response = requests.post(geStationDataURL, params=params)
        print('Response from Netatmo:\n',response)
        response.raise_for_status()
        data = response.json()['body']
        print('Data returned from Netatmo:\n',data)
    except requests.exceptions.HTTPError as error:
        # "Invalid access token" responce from netatmo
        # Request new token
        print('Some error occured.\nParams sendt:\n{}\nError code = {}\nError text =\n{}\nRetry initialization'.format(params,error.response.status_code, error.response.text))
        # Renew token?


    if ( netAtmoJsonData ):
        # write weather data to file
        try:
            with open( netatmoStationData,'w', encoding='utf-8') as dataFile:
                dataFile.write(json.dumps(data, indent=4))
            dataFile.close()
            if ( debugLevel1 ):
                print('Saved weather data:\n{}\nto {}'.format(json.dumps(data, indent=4),netatmoStationData))
        except Exception as e:
            # Data download from Netatmo failed 
            if ( debugLevel1 ):
                print(
                    'Debug level1:\nWether Data file not saved. {}. \
                        Problems generating file from your NetAtmo account.'.format(e))

    if ( debugLevel1 ):
        print('Debug level1:\ngetNetAtmo done')
    # End getNeatAtmoData
    # print('Respons keys',response.json().keys())
    return (response.json())


# main() # starts here

if ( debugLevel1 ):
    print('Tokendata before inetNetAtmo=\n', tokenData,'main() - netAtmoDeviceID=\n', netAtmoDeviceID)

returnValue = initNetAtmo(tokenData, netAtmoDeviceID)
tokenData = returnValue[0]
netAtmoDeviceID = returnValue[1]

if (debugLevel1):
    print('Tokendata after inetNetAtmo=\n', tokenData,'main() - netAtmoDeviceID=\n', netAtmoDeviceID)

netAtmoDeviceJsonData = getNetAtmoData(tokenData, netAtmoDeviceID)
print('Data downloaded?')
# downloading all NetAtmo data done
# Split out the interesting parts ['device'] and ['user']

netAtmoDeviceJsonDataDevices = netAtmoDeviceJsonData['body']['devices']
netAtmoDeviceJsonDataUser = netAtmoDeviceJsonData['body']['user']

if ( debugLevel1 ):
    # print result
    print('NetAtmo body data read:\n{}\n'.format(json.dumps(netAtmoDeviceJsonData, indent=4)))
    # Lets display some key data
    # in a pritty structure in 'device' and 'user'
    print('Station Data ["devices"]=\n{}'.format(json.dumps(netAtmoDeviceJsonDataDevices, indent=4)))
    print('Station Data ["user"]=\n{}'.format(json.dumps(netAtmoDeviceJsonDataUser, indent=4)))

netAtmoLocation = netAtmoDeviceJsonDataDevices[0]['station_name']
netAtmoTimeStamp = netAtmoDeviceJsonDataDevices[0]['last_status_store']
netAtmoDataType = netAtmoDeviceJsonDataDevices[0]['data_type']

netAtmoDashboardDataTime = netAtmoDeviceJsonDataDevices[0]['dashboard_data']['time_utc']
netAtmoDashboardTemp = netAtmoDeviceJsonDataDevices[0]['dashboard_data']['Temperature']
netAtmoDashboardPressure = netAtmoDeviceJsonDataDevices[0]['dashboard_data']['Pressure']
netAtmoDashboardCO2 = netAtmoDeviceJsonDataDevices[0]['dashboard_data']['CO2']
netAtmoDashboardHumidity = netAtmoDeviceJsonDataDevices[0]['dashboard_data']['Humidity']
netAtmoDashboardPressure = netAtmoDeviceJsonDataDevices[0]['dashboard_data']['Pressure']
netAtmoDashboardModulesModuleName1 = netAtmoDeviceJsonDataDevices[0]['modules'][0]['module_name']
netAtmoDashboardModulesDashboardTime = netAtmoDeviceJsonDataDevices[0]['modules'][0]['dashboard_data']['time_utc']
netAtmoDashboardModulesDashboardTemperature = netAtmoDeviceJsonDataDevices[0]['modules'][0]['dashboard_data']['Temperature']
netAtmoDashboardModulesDashboardHumidity = netAtmoDeviceJsonDataDevices[0]['modules'][0]['dashboard_data']['Humidity']
netAtmoDashboardModulesDashboardTempTrend = netAtmoDeviceJsonDataDevices[0]['modules'][0]['dashboard_data']['temp_trend']
netAtmoDashboardModulesModuleName2 = netAtmoDeviceJsonDataDevices[0]['modules'][1]['module_name']
netAtmoDashboardModulesRainDataType = netAtmoDeviceJsonDataDevices[0]['modules'][1]['data_type'][0]
netAtmoDashboardModulesRainDataTypeRain = netAtmoDeviceJsonDataDevices[0]['modules'][1]['dashboard_data']['Rain']

netatmoJsonLocalData = [{
    "Adress" : netAtmoLocation,
    "netatmoSensorTimeStamp" : time.ctime(netAtmoTimeStamp),
    "indorTemperature" : {"value" : netAtmoDashboardTemp, "unit" : "c" },
    "atmosphericPressure" : {"value" : netAtmoDashboardPressure, "unit" : "mbar" },
    "indorCO2Level" : { "value" : netAtmoDashboardCO2, "unit" : "ppm" }, 
    "indorHumidity" : { "value" : netAtmoDashboardHumidity, "unit" : "%" },
    "indorDataCaptureTimeStampe" : time.ctime(netAtmoDashboardDataTime),
    "outdorTemperature" : { "value" : netAtmoDashboardModulesDashboardTemperature, "unit" : "c" },
    "outdorTemperatureTrend" : { "value" : netAtmoDashboardModulesDashboardTempTrend, "unit" : "trend" },
    "outdorHumidity" : { "value" : netAtmoDashboardModulesDashboardHumidity, "unit" : "%" },
    "outdorPrecipitation" : netAtmoDashboardModulesRainDataType,
    "outdorAmount" : { "value" : netAtmoDashboardModulesRainDataTypeRain, "unit" : "mm" },
    "outdorPrecipitationTimeStamp" : time.ctime(netAtmoDashboardModulesDashboardTime)
}]

if ( debugLevel0 ):
    print('************* General *******************')
    print('Station name: {}'.format(netAtmoLocation))
    print('Time stamp: {}'.format(time.ctime(netAtmoTimeStamp)))
    print('************* Indor *******************')
    print('Data types: {}'.format(netAtmoDataType))
    print('Temperature: {}'.format(netAtmoDashboardTemp))
    print('Pressure: {}'.format(netAtmoDashboardPressure))
    print('CO2: {}'.format(netAtmoDashboardCO2))
    print('Humidity: {}'.format(netAtmoDashboardHumidity))
    print('Data captured at: {}'.format(time.ctime(netAtmoDashboardDataTime)))
    print('************* Outdor temperature, trend and humidity *******************')

    print('Capture data from: {}'.format(netAtmoDashboardModulesModuleName1))
    print('Temperature: {}'.format(netAtmoDashboardModulesDashboardTemperature))
    print('Temperature trend: {}'.format(netAtmoDashboardModulesDashboardTempTrend))
    print('Humidity: {}'.format(netAtmoDashboardModulesDashboardHumidity))

    print('************* Outdor rain/snow  *******************')
    print('Module name: {}'.format(netAtmoDashboardModulesModuleName2))
    print('"Nedbør" type: {}'.format(netAtmoDashboardModulesRainDataType))
    print('"Nedbør" ammount: {}'.format(netAtmoDashboardModulesRainDataTypeRain))
    print('Captured at: {}'.format(time.ctime(netAtmoDashboardModulesDashboardTime) ))
    
    #result
    print('Result (se also {}):\n{}'.format(resultJsonFile, json.dumps(netatmoJsonLocalData, indent=4, ensure_ascii=False)))

# Print result to file

try:
    with open(resultJsonFile, 'w', encoding='utf-8') as resultJsonFileWrite:
        resultJsonFileWrite.write(json.dumps(netatmoJsonLocalData, indent=4))
    resultJsonFileWrite.close()
except Exception as e:
    if debugLevel1:
        print('Error writing data to {}.\nError is:\n{}'.format(resultJsonFile,e))
    exit(e)
