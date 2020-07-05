#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import serial

SERIAL_PORT_NAME = "/dev/ttyUSB0"
SERIAL_PORT_BAUD = 38400
SERIAL_PORT_TIME_OUT = 60

ELM_CONNECT_SETTLE_PERIOD = 5
ELM_CONNECT_TRY_COUNT = 5

def GetResponse(SerialCon, Data):
    SerialCon.write(Data)
    Response = ""
    ReadChar = 1
    while ReadChar != b'>' and ReadChar != 0:
        ReadChar = SerialCon.read()
        if ReadChar != b'>':
            Response += str(ReadChar, 'utf-8')
    return Response.replace('\r', '').replace('\n\n', '')

def PruneData(Data, RemoveByteCount):
    Response = ""
    Lines = Data.split('\n')
    for Line in Lines:
        Response += Line[2 * RemoveByteCount:]
    return Response

ELM327 = serial.Serial(SERIAL_PORT_NAME, SERIAL_PORT_BAUD)
ELM327.timeout = SERIAL_PORT_TIME_OUT
ELM327.write_timeout = SERIAL_PORT_TIME_OUT
#print("Serial Port: " + ELM327.name.replace('\n', ''))

Response = GetResponse(ELM327, b'AT Z\r')
#print(Response.replace('\n', ''))

Response = GetResponse(ELM327, b'AT E0\r')
if Response != 'AT E0OK':
        print("FAILED: AT E0 (Echo Off)")

Response = GetResponse(ELM327, b'AT S0\r')
if Response != 'OK':
        print("FAILED: AT S0 (Space Characters Off)")

Response = GetResponse(ELM327, b'AT IB 10\r')
if Response != 'OK':
        print("FAILED: AT IB 10 (HS CAN)")

Response = GetResponse(ELM327, b'AT @1\r')
#print("ELM Description: " + Response.replace('\n', ''))

#print("CONNECTING TO OBDII...")
TryCount = 5
Response = "UNABLE TO CONNECT"
while Response.find("UNABLE TO CONNECT") != -1 and TryCount > 0:
    #TryCount -= 1
    #Count = ELM_CONNECT_SETTLE_PERIOD
    #while Count > 0:
        #sys.stdout.write('\r' + str(Count))
        #sys.stdout.flush()
        #time.sleep(1)
        #Count -= 1
    #sys.stdout.write('\r \r')
    #sys.stdout.flush()
    Response = GetResponse(ELM327, b'0100\r')
    if Response.find("UNABLE TO CONNECT") != -1:
        print("REATTEMPTING TO CONNECT... [" + str(TryCount) + "]")
if Response.find("UNABLE TO CONNECT") != -1:
    print("FAILED TO CONNECT TO CAN BUS")
    ELM327.close()
    quit()

#Response = GetResponse(ELM327, b'AT DP\r')
#print("Using CAN Bus Protocol: " + Response.replace('\n', ''))

try:
    def voltage():
        voltage = GetResponse(ELM327, b'AT RV\r')
        if voltage == "NO DATA":
            return str("N/A")
        else:
            try:
                return str(voltage.replace('\n', ''))
            except Exception as e:
                return str("N/A")

    def intake():
        Intake = GetResponse(ELM327, b'010F\r')
        if Intake == "NO DATA":
            return str("N/A")
        else:
            try:
                Intake = PruneData(Intake, 2)
                Intake = int(Intake, 16)
                Intake = Intake - 40
                return str(Intake)
            except Exception as e:
                return str("N/A")

    def load():
        Load = GetResponse(ELM327, b'0104\r')
        if Load == "NO DATA":
            x = GetResponse(ELM327, b'AT SI\r')
            return str("N/A")
        else:
            try:
                Load = PruneData(Load, 2)
                Load = int(Load, 16)
                Load = Load / 2.55
                Load = Load * 0.6
                return str("%.2f" % Load)
            except Exception as e:
                x = GetResponse(ELM327, b'AT SI\r')
                return str("N/A")

    def throttle():
        Throttle = GetResponse(ELM327, b'0111\r')
        if Throttle == "NO DATA":
            return str("N/A")
        else:
            try:
                Throttle = PruneData(Throttle, 2)
                Throttle = int(Throttle, 16)
                Throttle = Throttle / 2.55
                return str("%.2f" % Throttle)
            except Exception as e:
                return str("N/A")
except Exception as e:
    print(e)
