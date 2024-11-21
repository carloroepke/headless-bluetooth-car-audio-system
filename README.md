---    Work stopped 2018, newer projects are (and will stay) private ;)    ---

# headless-bluetooth-car-audio-system
I'm using a raspberry pi to create a truly headless bluetooth car audio system with some cool features for my old VW Polo Variant's car Stereo (VW gamma IV). This repository conatins all code for the media control, OBD readout and bluetooth functionality.

## 1 - necessary Hardware
* car radio with AUX input an control signal output (ideally an unlocked CD changer functionality)
* raspberry pi with WLAN and bluetooth (i used a raspberry 3 with raspbian stretch)
* bluetooth stick 
* USB soundcard 
* preamp
* ground loop isolation
* power management board: https://mausberry-circuits.myshopify.com/collections/car-power-supply-switches
* ELM 327 OBD reader
* small OLED screen

## 2 - Preparation of raspberry pi
I followed this guide and set up the raspberry for bluetooth audio: 
https://gist.github.com/mill1000/74c7473ee3b4a5b13f6325e9994ff84c

## 3 - understanding DBus
The linux system bus is called DBus. Here you can find the bluetooth related information like ID3-Tags and methods like pause and previous. I used a program called DFeet to navigate around in the filestructure of the DBus. This comes in handy later.

## 4 - accessing the DBus asyncronously via python


## 5 - sending the information onto the display
adafruit helps here :)

## 6 - understanding the protocol of the CD changer
https://martinsuniverse.de/projekte/cdc_protokoll/cdc_protokoll.html


## 7 - accessing the ECU of my car via OBD in python
