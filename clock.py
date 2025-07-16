from machine import Pin, ADC, I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from neopixel import NeoPixel
import time, onewire, ds18x20, pyRPiRTC, math, binascii, datetime, dht

#pinitialisation

#turn on LED to indicate initialisation
onboardLED = Pin(25, Pin.OUT)
onboardLED.value(1)

#assign pins
#28 - neopixel, 27 - light sensor, 26 - potentiometer, 20 - thermometer, 17 - OLED scl, 16, OLED sda
potentiometer = ADC(Pin(26))		#0-65535
lightSensor = ADC(Pin(27))			#0-65535
thermometerPin = Pin(20, Pin.IN)

#thermometer
thermometer = ds18x20.DS18X20(onewire.OneWire(thermometerPin))
thermometerRoms = thermometer.scan()

#dht
dhtDevice = dht.DHT11(Pin(22))
#dhtDevice = dht.DHT22(Pin(22))
#(dht11 max sampling rate of 1 sec, dht22 max sampling rate of 2 secs)

#led strip
ledStrip = NeoPixel(Pin(28), 15)

#lcd screen
SDA = 14
SCL = 15
I2C_BUS = 1
LCD_ADDR = 0x27

LCD_NUM_ROWS = 2
LCD_NUM_COLS = 16

lcdi2c = I2C(I2C_BUS, sda=machine.Pin(SDA), scl=machine.Pin(SCL), freq=400000)
lcd = I2cLcd(lcdi2c, LCD_ADDR, LCD_NUM_ROWS, LCD_NUM_COLS)

lcdString = "initialising! :^"
lcd.putstr(lcdString)

#rtc initialisation
rtc = pyRPiRTC.DS1302(clk_pin=19, data_pin=18, ce_pin=17)
#print(rtc.read_datetime())
#

onboardLED.value(0)


#initialising variables
hourCol = (255, 0, 0)
minCol = (0, 255, 0)
secCol = (0, 0, 255)
#variables used to store what is currently displayed
displayedString1 = ""	#line 1 of lcd
displayedString2 = ""	#line 2
currentLed = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]
ledArray = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]


def readRTC():
    currentTime = ""
    while currentTime == "":
        try:
            currentTime = str(rtc.read_datetime())
        except:
            print("RTC error, retrying")
    return currentTime

#interrupts--------------------------------------------------------------------------------------------------------

menuState: str = "HOME"	#home, menu, year, month, date, time
tempReading:str = "avg"	#avg, int, ext - average, internal thermo (dht11/22), external thermo (ds18... onewire)
menu1Selection:int = 0
currentDigit:int = 0
currentIndex:str = 0
newTime = [0,0,0,0]			#hour, min
newDate = [2,0,0,0,1,0,1]	#yyyymmdd
debounceTicks = 0

redPin = Pin(0, Pin.IN, Pin.PULL_UP)
greenPin = Pin(1, Pin.IN, Pin.PULL_UP)

month = ["","January         ", "February        ", "March           ", "April           ", "May             ",
                     "June            ", "July            ", "August          ", "September       ", "October         ", "November        ", "December        "]
def daysInMonth(month, year):
    if((month==2) and ((year%4==0)  or ((year%100==0) and (year%400==0)))):
        return 29
    elif(month==2):
        return 28
    elif(month==1 or month==3 or month==5 or month==7 or month==8 or month==10 or month==12):
        return 31
    else:
        return 30

def redInterrupt(pin):
    global menuState, tempReading, menu1Selection, lcd, debounceTicks, currentDigit, currentIndex, month
    #debounce check 500ms
    currentTicks = time.ticks_ms()
    if time.ticks_diff(currentTicks, debounceTicks) > 750:	#value can be edited depending on button used
        debounceTicks = currentTicks 
    else:
        return
        
    #print("red interrupt")
    
    if menuState == "HOME":
            if tempReading == "avg":
                tempReading = "int"
            elif tempReading == "int":
                tempReading = "ext"
            elif tempReading == "ext":
                tempReading = "avg"
                
    elif menuState == "MENU":
        if menu1Selection == 0:
            lcd.move_to(15, 1)
            menu1Selection = 1
        elif menu1Selection == 1:
            lcd.move_to(15, 0)
            menu1Selection = 0
            
    elif menuState == "TIME":
        #if statements to stop hours going above 23 and minutes going above 59
        #first digit can only be 0,1,2
        if currentIndex == 0:
            if currentDigit < 2:
                currentDigit += 1
            else:
                currentDigit = 0

        elif currentIndex == 1:
            #max hours is 23
            if newTime[0] == "2":
                if currentDigit < 3:
                    currentDigit += 1
                else:
                    currentDigit = 0
            else:
                if currentDigit < 9:
                    currentDigit += 1
                else:
                    currentDigit = 0
                    
        elif currentIndex == 2:
            #max minutes is 59
            if currentDigit < 5:
                currentDigit += 1
            else:
                currentDigit = 0
                    
        elif currentIndex == 3:
            if currentDigit < 9:
                currentDigit += 1
            else:
                currentDigit = 0
            
        
        lcd.putstr(str(currentDigit))
        #stop cursor from moving ahead when digit changes
        if currentIndex < 2:
            lcd.move_to(currentIndex, 1)
        else:
            lcd.move_to(currentIndex + 1, 1)
        
    elif menuState == "YEAR":
        if currentDigit < 9:
                currentDigit += 1
        else:
            currentDigit = 0
        lcd.putstr(str(currentDigit))
        lcd.move_to(currentIndex + 6, 0)
        
    elif menuState == "MONTH":
        #month is treated like a single digit 1-12
        if currentDigit < 12:
                currentDigit += 1
        else:
            currentDigit = 1
        lcd.move_to(0, 1)
        lcd.putstr(month[currentDigit])
        lcd.move_to(0, 0)
        lcd.putstr(str(currentDigit)+"              ")
        lcd.move_to(0, 0)
        
    elif menuState == "DATE":
        if currentIndex == 6:
            #check if month has > 29 days
            dayCount = daysInMonth(newDate[4], int(str(newDate[0])+str(newDate[1])+str(newDate[2])+str(newDate[3])))
            if (currentDigit < 2) or (dayCount > 29 and currentDigit < 3):
                currentDigit += 1
            else:
                currentDigit = 0
            
        else:	#(currentIndex = 7)
            dayCount = daysInMonth(newDate[4], int(str(newDate[0])+str(newDate[1])+str(newDate[2])+str(newDate[3])))
            #if 1st digit is 0, 1, 2 or 1st digit is 3 and month has 31 days and current digit is 0
            if (newDate[5] < 3 and currentDigit < 9) or (newDate[5] == 3 and dayCount == 31 and currentDigit == 0 ):
                currentDigit += 1
            #if 1st digit is 0, has to start from 1
            elif newDate[5] == 0:
                currentDigit = 1
            else:
                currentDigit = 0
        lcd.putstr(str(currentDigit))
        lcd.move_to(currentIndex, 0)
        

def grnInterrupt(greenPin):
    global debounceTicks, menuState, menu1Selection, lcd, rtc, newTime, newDate, currentDigit, currentIndex, displayedString1, displayedString2, month
    
    #debounce check 500ms
    currentTicks = time.ticks_ms()
    if time.ticks_diff(currentTicks, debounceTicks) > 1000:
        debounceTicks = currentTicks
    else:
        return
        
    #print("green interrupt")
    if menuState == "HOME":
        menuState = "MENU"
        #change date/time menu
        menu1Selection = 0
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Change Time")
        lcd.move_to(0, 1)
        lcd.putstr("Change Date")
        lcd.move_to(15, 0)
        lcd.show_cursor()
        lcd.blink_cursor_on()
        
    elif menuState == "MENU":
        if menu1Selection == 0:
            menuState = "TIME"
            #change time menu
            currentTime = readRTC()
            lcd.move_to(0, 1)
            lcd.putstr(currentTime[11:16]+"        ")
            newTime[0] = currentTime[11]
            newTime[1] = currentTime[12]
            newTime[2] = currentTime[14]
            newTime[3] = currentTime[15]
            lcd.move_to(0, 1)
            currentDigit = int(currentTime[11])
            currentIndex = 0
            
        else:
            menuState = "YEAR"
            #change date menu
            lcd.move_to(0, 0)
            currentTime = readRTC()
            newDate = [int(currentTime[0]), int(currentTime[1]), int(currentTime[2]), int(currentTime[3]), int(currentTime[5:7]), 0, 1]
            currentIndex = 2	#start at the 3rd digit of the year - rtc only goes up to 2099
            #TODO get a new rtc chip before 2099
            currentDigit = newDate[currentIndex]
            lcd.putstr("Year: " + currentTime[0:4] + "    ")
            lcd.move_to(currentIndex + 6, 0)
            
    elif menuState == "TIME":
        currentTime = readRTC()
        newTime[currentIndex] = str(currentDigit)
        if currentIndex < 3:
            currentIndex += 1
            if currentIndex < 2:
                currentDigit = int(currentTime[11 + currentIndex])
                lcd.move_to(currentIndex, 1)
            else:	#skip the : between hour and minute
                currentDigit = int(currentTime[12 + currentIndex])
                lcd.move_to(currentIndex + 1, 1)
        else:
            currentTime = readRTC()
            #writing new time, keeping current date
            rtc.write_datetime(datetime.datetime(int(currentTime[0:4]), int(currentTime[5:7]), int(currentTime[8:10]), int(newTime[0]+newTime[1]), int(newTime[2]+newTime[3])))
            #set back to displaying time
            lcd.hide_cursor()
            lcd.clear()
            menuState = "HOME"
            displayedString1 = ""	#line 1 of lcd
            displayedString2 = ""	#line 2
    
    elif menuState == "YEAR":
        newDate[currentIndex] = currentDigit
        currentIndex += 1
        if currentIndex < 4:	#year is 4 characters
            lcd.move_to(currentIndex + 6, 0)
            currentDigit = newDate[currentIndex]
        else:
            menuState = "MONTH"
            currentDigit = newDate[4]
            lcd.hide_cursor()
            lcd.move_to(0, 1)
            lcd.putstr(month[newDate[4]])
            lcd.move_to(0, 0)
            lcd.putstr(str(newDate[4])+"              ")
            lcd.move_to(0, 0)
        
    elif menuState == "MONTH":	#month treated as 1 character
        menuState = "DATE"
        #save month and move onto first digit of date
        newDate[4] = currentDigit
        newDate[5] = 0
        newDate[6] = 1
        currentDigit = 0
        currentIndex = 6
        lcd.move_to(0, 0)
        lcd.putstr("Date: 01")
        lcd.move_to(6, 0)
        lcd.show_cursor()
        lcd.blink_cursor_on()
        
    
    elif menuState == "DATE":
        #set first digit of date
        if currentIndex == 6:
            newDate[5] = currentDigit
            #move to last digit
            currentIndex = 7
            currentDigit = newDate[6]
            #change 2nd digit if days are too high (30 or 31)
            dayCount = daysInMonth(newDate[4], int(str(newDate[0])+str(newDate[1])+str(newDate[2])+str(newDate[3])))
            #if date is 3X and either month has 31 days and X > 1 or month has 30 days, make X = 0
            if newDate[5] == 3 and ( (dayCount == 31 and currentDigit > 1) or (dayCount == 30) ):
                currentDigit = 0
                newDate[6] = 0
                lcd.move_to(7, 0)
                lcd.putstr("0")
            else:
                currentDigit = newDate[6]
            lcd.move_to(7, 0)
        else:
            #set second digit of date
            newDate[6] = currentDigit
            #writing new date, keeping current time
            currentTime = readRTC()
            rtc.write_datetime(datetime.datetime(int(str(newDate[0])+str(newDate[1])+str(newDate[2])+str(newDate[3])), newDate[4], int(str(newDate[5])+str(newDate[6])), int(currentTime[11:13]), int(currentTime[14:16])))
            #set back to displaying time
            lcd.hide_cursor()
            lcd.clear()
            menuState = "HOME"
            displayedString1 = ""	#line 1 of lcd
            displayedString2 = ""	#line 2
            

redPin.irq(trigger=Pin.IRQ_FALLING, handler=redInterrupt)
greenPin.irq(trigger=Pin.IRQ_FALLING, handler=grnInterrupt)


#main ==============================================================================================================================

time.sleep(1)
lcd.clear()

while True:
    #get current time and format into string
    #print("current time: " + str(rtc.read_datetime()))
    currentTime = readRTC()
    lcdString1 = currentTime[11:16] + "   " + currentTime[8:10] + "/" + currentTime[5:7] + "/" + currentTime[2:4]
    hours = int(currentTime[11:13])
    mins = int(currentTime[14:16])
    secs = int(currentTime[17:19])
    
    #Brightness calculations ---------------------------------------------------------------------------------------------------------------------
    potPercent = (potentiometer.read_u16() / 65535) * 100
    lightPercent = (lightSensor.read_u16() / 66000) * 100 #divide by larger value so light can be turned off easily
    #if light level is higher than potentiometer then keep light on, pot used for light tolerance
    if lightPercent > potPercent:
        lcd.backlight_on()
        ledMultiplier = round(1 - (potPercent / lightPercent), 2)
        #print("light")
    else:
        lcd.backlight_off()
        ledMultiplier = 0
        #print("dark")
    #print(str(ledMultiplier))
    
    #print("pot - " + str(potentiometer.read_u16()) + ", " + str(potPercent) + "%")
    #print("light - " + str(lightSensor.read_u16()) + ", " + str(lightPercent) + "%")
    #print("time - " + str(rtc.read_datetime()))
    
    
    #led array assignment
    for item in range(len(ledArray)):
        ledArray[item] = (0, 0, 0)	#reset led values
    #calculate which led each clock hand is on and multiply their colour by global multiplier, and add to existing colour
    ledArray[hours % 12] = (round(hourCol[0] * ledMultiplier), round(hourCol[1] * ledMultiplier), round(hourCol[2] * ledMultiplier))
    ledArray[mins // 5] = tuple(map(lambda i, j: i + j, ledArray[mins // 5], (round(minCol[0] * ledMultiplier), round(minCol[1] * ledMultiplier), round(minCol[2] * ledMultiplier))))
    ledArray[secs // 5] = tuple(map(lambda i, j: i + j, ledArray[secs // 5], (round(secCol[0] * ledMultiplier), round(secCol[1] * ledMultiplier), round(secCol[2] * ledMultiplier))))
    
    
    #lcd readout ---------------------------------------------------------------------------------------------------------------------------------------------------
    
    #reading dht temp + humidity
    dhtSuccess = False
    try:
        dhtDevice.measure()
        dhtSuccess = True
        #print(" temp: " + str(dhtDevice.temperature()) + " humidity: " + str(dhtDevice.humidity()))
    except OSError as e:
        print('Failed to read dht sensor')
    
    #getting temperature and adding to string
    thermometer.convert_temp()
    for rom in thermometerRoms:
        print((thermometer.read_temp(rom)),"C")
        
    #deciding which temperature sensor to use, 13th led indicating dht, 14th indicating onewire
    if tempReading == "avg" and dhtSuccess:
        lcdString2 = str(round((thermometer.read_temp(rom) + dhtDevice.temperature() )/ 2, 1))
        ledArray[12] = (round(hourCol[0] * ledMultiplier), round(hourCol[1] * ledMultiplier), round(hourCol[2] * ledMultiplier))
        ledArray[13] = (round(minCol[0] * ledMultiplier), round(minCol[1] * ledMultiplier), round(minCol[2] * ledMultiplier))
    elif tempReading == "int" or not dhtSuccess:
        lcdString2 = str(round(float(dhtDevice.temperature()), 1)) #dht11 only gives integer, needs to be converted to float
        ledArray[12] = (round(hourCol[0] * ledMultiplier), round(hourCol[1] * ledMultiplier), round(hourCol[2] * ledMultiplier))
        ledArray[13] = (0, 0, 0)
    elif tempReading == "ext":
        lcdString2 = str(round(thermometer.read_temp(rom), 1))
        ledArray[12] = (0, 0, 0)
        ledArray[13] = (round(minCol[0] * ledMultiplier), round(minCol[1] * ledMultiplier), round(minCol[2] * ledMultiplier))
    
    lcdString2 += " C       " + str(dhtDevice.humidity()) + "%"
    
    
    #lcd
    #print("----------------")
    #print(lcdString1)
    #print(lcdString2)
    #print("----------------")
    
    #assigning leds
    if currentLed != ledArray:	#check if anything needs changing to prevent flickering
        for item in range(len(ledArray)):
            ledStrip[item] = ledArray[item]
            currentLed[item] = ledArray[item]
            ledArray[item] = (0, 0, 0)
        ledStrip.write()
    
    #writing to screen
    if menuState == "HOME":		#do not write to screen if in settings menu
        if lcdString1 != displayedString1:
            lcd.move_to(0, 0)
            lcd.putstr(lcdString1)
            displayedString1 = lcdString1
        if lcdString2 != displayedString2:
            lcd.move_to(0, 1)
            lcd.putstr(lcdString2)
            displayedString2 = lcdString2
    
    
    time.sleep(1)