#!/usr/bin/env python3

# read date and time from RTC chip, return ISO 8601 UTC string
# assume DS1302 contain UTC time and not local

import sys
import pyRPiRTC
import datetime

rtc = pyRPiRTC.DS1302(clk_pin=19, data_pin=18, ce_pin=17)

try:
    # read date and time from RTC chip
    dt = rtc.read_datetime()
    print("current time: " + str(rtc.read_datetime()))
except ValueError:
    sys.exit('error with RTC chip, check wiring')
finally:
    # clean close
    rtc.close()
