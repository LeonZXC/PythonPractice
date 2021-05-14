# Basic MacOS Log Decoder
# Author: Leonard
# Last Update: 14/05/2021

# import requests
import json
import re
from datetime import datetime, timedelta
from typing import get_type_hints
import requests

# Read in raw log, handle broken line cases
rawLog = input("Provide file path: ")
with open(rawLog, 'r') as logFile:
    logs = []
    for line in logFile.read().split('\n'):
        if not re.search("^/s", line):
            logs.append(line)
        else:
            logs[-1] += '\n' + line

# Perform regex operations and extract fields
output = []
url = "https://foo.com/bar"
for line in logs:
    # Check if launchd process for dedicated regex, otherwise general
    launchdCheck = re.search('launchd\[1\]', line)
    if (launchdCheck):
        match = re.search("(?P<timestamp>\w{3}\s\d{2}\s\d{2}:\d{2}:\d{2})\s(?P<hostname>\w+)\s(?P<processName>.*)\[(?P<processID>\d+)\].*\):(?P<description>.*)", line)
    else:
        match = re.search("(?P<timestamp>\w{3}\s\d{2}\s\d{2}:\d{2}:\d{2})\s(?P<hostname>\w+)\s(?P<processName>.*)\[(?P<processID>\d+)\].*:(?P<description>.*)", line)
    if match:
        # Create timeWindow key from timestamp
        timeStr = str(match.group('timestamp'))
        dTime = datetime.strptime(timeStr, '%b %d %H:%M:%S')
        plusHour = dTime + timedelta(hours=1)
        dTimeStr = str(dTime.hour) 
        plusHourStr = str(plusHour.hour)
        if len(dTimeStr) == 1:
            dTimeStr = "0" + dTimeStr
        if len(plusHourStr) == 1:
            plusHourStr = "0" + plusHourStr
        hourWindow = dTimeStr + "00-" + plusHourStr + "00"

        # Add regex field keys to dictionary
        fields = {
            'timestamp': match.group('timestamp'),
            'timeWindow': hourWindow,
            'deviceName': match.group('hostname'),
            'processName': match.group('processName'),
            'processId': match.group('processID'),
            'description': match.group('description'),
            'numberOfOccurrence': 0
        }
        # Checks if devices have same requirements to consider as repeated occurrence
        # Checks deviceName, timeWindow, processId and message description

        # If list is not empty
        if output:
            for fieldDict in output:
                if ((fieldDict['deviceName'] in fields.values()) and (fieldDict['timeWindow'] in fields.values()) and (fieldDict['processId'] in fields.values()) and (fieldDict['description'] in fields.values())):
                    fields['numberOfOccurrence'] = fieldDict.get('numberOfOccurrence', 0) + 1
                else:
                    fields['numberOfOccurrence'] = 1
            output.append(fields)
            fieldsJSON = json.dumps(fields) 
            requests.post(url, data=fieldsJSON)
        # If list is empty
        else:
            fields['numberOfOccurrence'] = fields.get('numberOfOccurrence', 0) + 1
            output.append(fields)
            fieldsJSON = json.dumps(fields)
            requests.post(url, data=fieldsJSON)