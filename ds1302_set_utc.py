#!/usr/bin/env python3

# write RPi current date and time (UTC time) to DS1302 RTC chip
# read value after write to check update

import datetime
import sys
import pyRPiRTC
import time

rtc = pyRPiRTC.DS1302(clk_pin=19, data_pin=18, ce_pin=17)

try:
    # write date and time from system to RTC chip (in UTC)
    #year, month, day, hour, min
    dt_write = datetime.datetime(2025, 7, 10, 14, 53)
    print(dt_write)
    # update rtc
    rtc.write_datetime(dt_write)
    # check update is good
    dt_read = rtc.read_datetime()
    if -2 < (dt_write - dt_read).total_seconds() < +2:
        print("current time set: " + str(rtc.read_datetime()))
    else:
        exit('unable to set RTC time')
except ValueError:
    sys.exit('error with RTC chip, check wiring')
finally:
    rtc.close()
