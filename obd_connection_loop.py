#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import time
import serial
import dbus
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)

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
    return Response.replace('\r', '\n').replace('\n\n', '\n')

def PruneData(Data, RemoveByteCount):
    Response = ""
    Lines = Data.split('\n')
    for Line in Lines:
        Response += Line[2 * RemoveByteCount:]
    return Response

ELM327 = serial.Serial(SERIAL_PORT_NAME, SERIAL_PORT_BAUD)
ELM327.timeout = SERIAL_PORT_TIME_OUT
ELM327.write_timeout = SERIAL_PORT_TIME_OUT
print("Serial Port: " + ELM327.name.replace('\n', ''))

Response = GetResponse(ELM327, b'AT Z\r')
print(Response.replace('\n', ''))

Response = GetResponse(ELM327, b'AT E0\r')
if Response != 'AT E0\nOK\n':
        print("FAILED: AT E0 (Echo Off)")

Response = GetResponse(ELM327, b'AT S0\r')
if Response != 'OK\n':
        print("FAILED: AT S0 (Space Characters Off)")

Response = GetResponse(ELM327, b'AT IB 10\r')
if Response != 'OK\n':
        print("FAILED: AT IB 10 (HS CAN)")

Response = GetResponse(ELM327, b'AT @1\r')
print("ELM Description: " + Response.replace('\n', ''))

print("CONNECTING TO OBDII...")
TryCount = 5
Response = "UNABLE TO CONNECT"
while Response.find("UNABLE TO CONNECT") != -1 and TryCount > 0:
    TryCount -= 1
    Count = ELM_CONNECT_SETTLE_PERIOD
    while Count > 0:
        sys.stdout.write('\r' + str(Count))
        sys.stdout.flush()
        time.sleep(1)
        Count -= 1
    sys.stdout.write('\r \r')
    sys.stdout.flush()
    Response = GetResponse(ELM327, b'0100\r')
    if Response.find("UNABLE TO CONNECT") != -1:
        print("REATTEMPTING TO CONNECT... [" + str(TryCount) + "]")
if Response.find("UNABLE TO CONNECT") != -1:
    print("FAILED TO CONNECT TO CAN BUS")
    ELM327.close()
    quit()

Response = GetResponse(ELM327, b'AT DP\r')
print("Using CAN Bus Protocol: " + Response.replace('\n', ''))

# Response = GetResponse(ELM327, b'0105\r')
# Response = PruneData(Response, 2)
# Response = int(Response, 16)
# Response = Response - 40
# print("Coolant Temp: " + str(Response))
#
# Response = GetResponse(ELM327, b'010C\r')
# Response = PruneData(Response, 2)
# Response = int(Response, 16)
# Response = Response / 4
# print("Engine RPM: " + str(Response))

mainloop = GObject.MainLoop()
context = mainloop.get_context()
while mainloop is not None:
    if context.pending():
        context.iteration()

    else:
        try:
            Voltage = GetResponse(ELM327, b'AT RV\r')
            print("Voltage: " + Voltage.replace('\n', ''))

            Intake = GetResponse(ELM327, b'010F\r')
            Intake = PruneData(Intake, 2)
            Intake = int(Intake, 16)
            Intake = Intake - 40
            print("Intake Temp: " + str(Intake) + u'\u00b0' + "C")

            Load = GetResponse(ELM327, b'0104\r')
            Load = PruneData(Load, 2)
            Load = int(Load, 16)
            Load = Load / 2.55
            Load = Load * 0.6
            print("Calculated Engine Load: " + str("%.2f" % Load) + "PS")

            Throttle = GetResponse(ELM327, b'0111\r')
            Throttle = PruneData(Throttle, 2)
            Throttle = int(Throttle, 16)
            Throttle = Throttle / 2.55
            print("Throttle Position: " + str("%.2f" % Throttle) + "%")
        except Exception as e:
            print(e)
