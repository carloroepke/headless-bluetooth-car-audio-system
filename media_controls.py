#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import dbus
import pigpio
import ir_hasher
import dbus_connection

from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

GObject.threads_init()
dbus.mainloop.glib.threads_init()
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
mainloop = GObject.MainLoop()

x = dbus_connection.connect_to_dbus_bluez()
x.load_player(x.bus, x.service, x.hci0_path)
        

def wait():
    print("warte...")

GObject.timeout_add(1000, wait)
context = mainloop.get_context()

os.system('sudo pigpiod')

hashes = {
  4290810019: 'Pause',      1293326593: 'Play',     508228451: 'Next',
  1337438801: 'Previous',   210910201: '1',         474387707: '2',
  1827856689: '3',          3277666307: '4',        2850547353: '5',
  1226072979: '6',          1220758985: 'FR',       4210471931: 'FF',
  4240395897: 'Pause CD',   3706158987: 'Play CD'   }

while mainloop is not None:
    if context.pending():
        context.iteration()
    else:
      if x.connect() != None:
        #print('TITLE ' + x.connect()[0] + ' & ' + x.connect()[1])

        def callback(hash):
          #print("hello")
          #print("hash = {}".format(hash))
          if hash in hashes:
             print("key = {} hash = {}".format(hashes[hash], hash))
             try:
                if hashes[hash] == 'Play':
                   x.ctrl_iface.Play()
                   print('Play')
                if hashes[hash] == 'Pause':
                   x.ctrl_iface.Pause()
                   print('Pause')
                if hashes[hash] == 'Next':
                   x.ctrl_iface.Next()
                   print('Next')
                if hashes[hash] == 'Previous':
                   x.ctrl_iface.Previous()
                   print('Previous')
             except Exception as e:
                print(e)
        pi = pigpio.pi()
        ir = ir_hasher.hasher(pi, 4, callback, 5)
        time.sleep(1)
        pi.stop()
        
      else:
            print("search for player...")
            x.load_player(x.bus, x.service, x.hci0_path)
            time.sleep(1)

