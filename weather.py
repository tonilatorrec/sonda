#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import gettext

from PyQt6.QtWidgets import QApplication
import serial

from gui import App

_ = gettext.gettext

def main(test=True, mode='test', port=0, api=0, channel=0):
    app = QApplication(sys.argv)
    App(test, mode, port, api, channel)  # main window
    sys.exit(app.exec())

if __name__ == '__main__':

    ap = argparse.ArgumentParser()

    ap.add_argument("-t", "--test", required=False, action="store_true",
                    help=_("Enables test mode"))
    ap.add_argument("-p", "--port", required=False,
                    help="Receive data from serial port")
    ap.add_argument("-b", "--baud", required=False,
                    help="Baud rate of the serial port")
    ap.add_argument("-a", "--api", help="Receive data from ThingSpeak API")

    args = ap.parse_args()

    if args.port and args.api:
        print("""Both serial port and API are given. You can only get data
                  from one source.""")
        # TODO: Ask which source to select, or if one source is not available
        # receive data from the other one.

    if len(sys.argv) == 1:
        run_mode = input("You must select one mode. Do you want to run in test mode? (y/n)\n> ")
        if run_mode == "y":
            main(args.test, mode='test')
        else:
            sys.exit()
    elif not(args.port and args.baud) and not (args.test or args.api):
        if not args.baud:
            try:
                args.baud = int(input("You must specify the baud rate (default is 9600):\n> "))
            except ValueError:
                args.baud = 9600
        elif not args.port:
            args.port = input("You must specify the port:\n> ")
        try:
            print(f"Listening to serial port at {args.port}")
            ser = serial.Serial(args.port, args.baud)
            main(args.test, mode='serial', port=args.port)
        except serial.serialutil.SerialException:
            print(f"Port at {args.port} is not available")
            sys.exit()
    elif args.api:
        api = args.api
        channel = input('ThingSpeak channel:\n> ')
        print(f'Listening to ThingSpeak channel {channel}')
        main(args.test, mode='api', api=api, channel=channel)
    else:
        main(args.test, mode='test')
