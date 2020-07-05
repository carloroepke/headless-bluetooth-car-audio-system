#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dbus
import sys
import os
import time
import math
import asyncio
import threading

import dbus_connection
import obd_connection

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from gi.repository import GObject
from xml.etree import ElementTree
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

# bluealsa-aplay -vv 00:00:00:00:00:00

# Constants -----------------------------------------------------------------------------
RST = 24                                                # RST Pin
DC = 23                                                 # DC Pin
SPI_PORT = 0                                            # SPI Port
SPI_DEVICE = 0                                          # SPI Device
DISP = Adafruit_SSD1306.SSD1306_128_64(rst=RST)         # Display Type

FONT = ImageFont.truetype('Montserrat-Regular.ttf', 8)  # Font
IMAGE = 'vw_logo_2.png'                                 # splash screen image

# Main Loop init -------------------------------------------------------------------------
disp = DISP # assign constant to working var
disp.begin()

disp.clear()
disp.display()

image = Image.open(IMAGE).convert('1')

disp.image(image)
disp.display()
time.sleep(3)

disp.clear()
disp.display()

width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

GObject.threads_init()
dbus.mainloop.glib.threads_init()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
mainloop = GObject.MainLoop()

#------------------------------------------------------------------------------------------
def show_connection(name, typ):
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.rectangle((10, 10, width-10, height-20), outline=255, fill=0)

    maxwidth1, unused = draw.textsize("connected to", font=FONT)
    maxwidth2, unused = draw.textsize(name + " " + typ, font=FONT)

    draw.text((64-(maxwidth1/2), 15), "connected to", font=FONT, fill=255)
    draw.text((64-(maxwidth2/2), 25), name + " " + typ, font=FONT, fill=255)

    disp.image(image)
    disp.display()

    time.sleep(3)

    draw.rectangle((0,0,width,height), outline=0, fill=0)
    disp.display()

def show_obd2():
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.text((10, 10), "V:  " + obd_connection.voltage(), font=ImageFont.truetype('Montserrat-Regular.ttf', 10) , fill=255) # momentane Leistung
    draw.text((10, 30), "C:  " + obd_connection.intake(), font=ImageFont.truetype('Montserrat-Regular.ttf', 10) , fill=255) # momentaner Drehmoment
    draw.text((70, 10), "PS: " + obd_connection.load(), font=ImageFont.truetype('Montserrat-Regular.ttf', 10) , fill=255) # momentane Ansaugtemperatur
    draw.text((70, 30), "%:  " + obd_connection.throttle(), font=ImageFont.truetype('Montserrat-Regular.ttf', 10) , fill=255) # momentaner Verbrauch

def no_dev_screen():
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    draw.rectangle((10, 62, width-10, height-20), outline=255, fill=0)

    maxwidth1, unused = draw.textsize("no device", font=FONT)

    draw.text((64-(maxwidth1/2), 48), "no device", font=FONT, fill=255)

    disp.image(image)
    disp.display()

    time.sleep(3)

    draw.rectangle((0,0,width,height), outline=0, fill=0)
    disp.display()

x = dbus_connection.connect_to_dbus_bluez()
x.load_player(x.bus, x.service, x.hci0_path)

def display_dev():
    if x.get_managed_objects() != None:
        try:
            show_connection(x.get_managed_objects()[0], x.get_managed_objects()[1])
            print ("connected to: " + x.get_managed_objects()[0] + " " + x.get_managed_objects()[1])
        except TypeError as e:
            #print (e)
            no_dev_screen()
            print ("no device connected!")

    else:
        no_dev_screen()
        print ("no device connected!")

display_dev()

def wait():
    print("warte...")

GObject.timeout_add(1000, wait)
context = mainloop.get_context()

#------------------------------------------------------------------------------------------
def pos_dur():
    draw.rectangle((width-35, height, width, 35), outline=255, fill=0)
    draw.text((width-35, height-10), str(pos) + '/' + str(dur), font=FONT, fill=255)

# Draw two rectangles.
def pause_sign():
    padding = 1
    shape_width = 5
    x = padding
    draw.rectangle((1, 54, 12, 64), outline=0, fill=0)
    draw.rectangle((x, 54, x+2, 64), outline=255, fill=255)
    x += shape_width+padding

    draw.rectangle((x, 54, x+2, 64), outline=255, fill=255)
    x += shape_width+padding

# Draw a square.
def stop_sign():
    padding = 1
    shape_width = 5
    x = padding
    draw.rectangle((1, 54, 12, 64), outline=0, fill=0)
    draw.rectangle((x, 54, 10, 64), outline=255, fill=255)
    x += shape_width+padding


# Draw a triangle.
def play_sign():
    padding = 1
    shape_width = 5
    x = padding
    draw.rectangle((1, 54, 12, 64), outline=0, fill=0)
    draw.polygon([(x, 64), (x, 54), (x+5, 59)], outline=255, fill=255)
    x += shape_width+padding

#animate text (title) if too long
async def anim_text(text):
    try:
        maxwidth, unused = draw.textsize(text, font=FONT)
        velocity = -5
        startpos = width
        pos = startpos

        while True:
            draw.rectangle((15, 53, width, height), outline=0, fill=0)
            
            if x.connect()[5] == "playing":
                play_sign()
            elif x.connect()[5] == "paused":
                pause_sign()
            elif x.connect()[5] == "stopped":
                stop_sign()
            show_obd2()

            if maxwidth > width-15:
                pos_x = pos
                for i, c in enumerate(text):
                    if pos_x > width:
                        break
                    if pos_x < 15:
                        char_width, char_height = draw.textsize(c, font=FONT)
                        pos_x += char_width
                        continue
                    draw.text((pos_x, height-10), c, font=FONT, fill=255)
                    char_width, char_height = draw.textsize(c, font=FONT)
                    pos_x += char_width

                disp.image(image)
                disp.display()
                pos += velocity
                if pos < -maxwidth-15:
                    pos = startpos
                    break
            else:
                draw.text((15, height-10), text, font=FONT, fill=255)
                disp.image(image)
                disp.display()
                time.sleep(1)
                break
    except TypeError as e:
        #print(e)
        display_dev()
#------------------------------------------------------------------------------------------

def time_conv(millisecs):
    secs  = format((int((millisecs/1000)%60)), '02d')
    mins  = int(millisecs/(1000*60)%60)
    timeout = str("{0}:{1}".format(mins, secs))
    return timeout

eventloop = asyncio.get_event_loop()

while mainloop is not None:
    if context.pending():
        context.iteration()
    else:
        if x.connect() != None:
            try:
                #os.system('clear')
                print('')
                try:
                    dur = time_conv(x.connect()[3])
                    pos = time_conv(x.connect()[4])
                except Exception as e:
                    print (e)

                eventloop.run_until_complete(anim_text(x.connect()[0] + " - " + x.connect()[1]))

                print ("--------------------------")
                print ("Current Track:")

                print ("Title: " + x.connect()[0])

                print ("Artist: " + x.connect()[1])

                print ("Album: " + x.connect()[2])

                print ("Position: " + str(pos))

                print ("Länge: " + str(dur))

                print ("Status: " + x.connect()[5])

                print ("connected to: " + x.get_managed_objects()[0] + " " + x.get_managed_objects()[1])

                print ("--------------------------")

                #time.sleep(1)
            except TypeError as e:
                #print(e)
                display_dev()
                eventloop.stop()

        else:
            display_dev()
            print("search for player...")
            eventloop.stop()
            x.load_player(x.bus, x.service, x.hci0_path)
            time.sleep(1)
