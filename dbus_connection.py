#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dbus
import sys
import os
import time
import math
import asyncio
import threading

from gi.repository import GObject
from xml.etree import ElementTree
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

BUS = dbus.SystemBus()                                  # DBus System Bus
SERVICE = 'org.bluez'                                   # Bluez Bluetooth Stack Service
HCI0_PATH = '/org/bluez/hci0'                           # Pfad zu integr. Bluetooth module
INTROSP_IFACE = 'org.freedesktop.DBus.Introspectable'   # Introspectable DBus Interface
MEDIA_IFACE = 'org.bluez.MediaPlayer1'                  # Bluez Media Interface
PROPS_IFACE = 'org.freedesktop.DBus.Properties'         # DBus Properties Interface
OBJECT_MANAGER = 'org.freedesktop.DBus.ObjectManager'   # Bluez Object Manager
DEVICE_1 = 'org.bluez.Device1'                          # Bluez Device Interface

class connect_to_dbus_bluez(object):
"""
this class contains all the necessary functions for you to hook onto the DBus Bluez object and search for bluetooth audio sources. 
if it finds an audio source it will keep track of specified attributes which are:
    Title       - Title of the song as String
    Artist      - Artist of the song as String
    Album       - Album of the song as String
    Duration    - duration of the song in ms
    Position    - how much time is elapsed? in ms   
    Status      - play or pause
"""


    def __init__(self):
        #set the class attributes to previously defined constants (TODO: move constants to own file)

        self.bus = BUS
        self.service = SERVICE
        self.hci0_path = HCI0_PATH
        self.mac = ""
        self.player = ""
        self.ctrl_iface = ""

    def load_player(self, bus, service, object_path):
        """
        this method checks if there is a player marked in the object path and then it extracts the MAC adress and the player interface. 
        otherwise it will keep recursively searching for a player.
        """

        if "player" in object_path:
            x = object_path.split("/")
            self.mac = x[4]
            self.player = x[5]
        obj = bus.get_object(service, object_path)
        iface = dbus.Interface(obj, INTROSP_IFACE)
        xml_string = iface.Introspect()
        for child in ElementTree.fromstring(xml_string):
            if child.tag == 'node':
                if object_path == '/':
                    object_path = ''
                new_path = '/'.join((object_path, child.attrib['name']))
                try:
                    self.load_player(bus, service, new_path)
                except Exception as e:
                    print(e)


    def connect(self):
        """
        this method connects to the found player and extracts the properties .
        """

        full_player_path = self.hci0_path + '/' + self.mac + '/' + self.player
        media_interface = MEDIA_IFACE
        try:
            device = self.bus.get_object(self.service, full_player_path)
            props_iface = dbus.Interface(device, PROPS_IFACE)
            properties = props_iface.GetAll(media_interface)
            self.ctrl_iface = dbus.Interface(device, media_interface)

            track = self.get_properties(properties, 'Track')
            title = self.get_properties(track, 'Title')
            artist = self.get_properties(track, 'Artist')
            album = self.get_properties(track, 'Album')
            duration = self.get_properties(track, 'Duration')
            pos = self.get_properties(properties, 'Position')
            status = self.get_properties(properties, 'Status')

            info = title, artist, album, duration, pos, status

            return info
        except Exception as e:
            return None

    def get_properties(self, dictionary, key):
        value = dictionary.get(key)
        if value == None:
            return ""
        else:
            return value

    def get_managed_objects(self):
        """
        this method extracts the managed objects from the specified constant DEVICE.
        """

        obj = self.bus.get_object(self.service, "/")
        iface = dbus.Interface(obj, OBJECT_MANAGER)
        objects = iface.GetManagedObjects()
        path = self.hci0_path + "/" + self.mac
        info = objects.get(path)
        if info != None:
            dev = info.get(DEVICE_1)
            name = dev.get("Name")
            ico = dev.get("Icon")
            connect = dev.get("Connected")
            if connect:
                out = name, ico
                return out
            else: return None
