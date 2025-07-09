from machine import Pin, ADC, I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
from neopixel import NeoPixel
import time, onewire, ds18x20, pyRPiRTC, math, binascii, datetime

def truncate(num, decimals = 0):
    return int((num * (10**decimals))/(10**decimals))

#turn on LED to indicate initiation
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
print(rtc.read_datetime())
#


onboardLED.value(0)


#initialising variables
hourCol = (255, 0, 0)
minCol = (0, 255, 0)
secCol = (0, 0, 255)
#variables used to store what is currently displayed
displayedString1 = ""
displayedString2 = ""
currentLed = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]
ledArray = [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)]

time.sleep(1)
lcd.clear()
while True:
    #get current time and format into string
    currentTime = str(rtc.read_datetime())
    lcdString1 = currentTime[11:16] + "   " + currentTime[8:10] + "/" + currentTime[5:7] + "/" + currentTime[2:4]
    hours = int(currentTime[11:13])
    mins = int(currentTime[14:16])
    secs = int(currentTime[17:19])
    
    #getting temperature and adding to string
    thermometer.convert_temp()
    for rom in thermometerRoms:
        print((thermometer.read_temp(rom)),"C")
    lcdString2 = str(round(thermometer.read_temp(rom), 1))
    lcdString2 += " C"
    
    
    #light stuff
    potPercent = (potentiometer.read_u16() / 65535) * 100
    lightPercent = (lightSensor.read_u16() / 66000) * 100 #divide by larger value so light can be turned off easily
    #if light level is higher than potentiometer then keep light on, pot used for light tolerance
    if lightPercent > potPercent:
        lcd.backlight_on()
        ledMultiplier = truncate(1 - (potPercent / lightPercent), 1)
        print("light")
    else:
        lcd.backlight_off()
        ledMultiplier = 0
        print("dark")
    print(str(ledMultiplier))
    
    print("pot - " + str(potentiometer.read_u16()) + ", " + str(potPercent) + "%")
    print("light - " + str(lightSensor.read_u16()) + ", " + str(lightPercent) + "%")
    print("time - " + str(rtc.read_datetime()))
    
    
    #led 
    for item in range(len(ledArray)):
        ledArray[item] = (0, 0, 0)
    ledArray[hours % 12] = (truncate(hourCol[0] * ledMultiplier), truncate(hourCol[1] * ledMultiplier), truncate(hourCol[2] * ledMultiplier))
    ledArray[mins // 5] = tuple(map(lambda i, j: i + j, ledArray[mins // 5], (truncate(minCol[0] * ledMultiplier), truncate(minCol[1] * ledMultiplier), truncate(minCol[2] * ledMultiplier))))
    ledArray[secs // 5] = tuple(map(lambda i, j: i + j, ledArray[secs // 5], (truncate(secCol[0] * ledMultiplier), truncate(secCol[1] * ledMultiplier), truncate(secCol[2] * ledMultiplier))))
    
    #lcd
    print("----------------")
    print(lcdString1)
    print(lcdString2)
    print("----------------")
    
    #assigning
    if currentLed != ledArray:
        for item in range(len(ledArray)):
            ledStrip[item] = ledArray[item]
            currentLed[item] = ledArray[item]
            ledArray[item] = (0, 0, 0)

        
        ledStrip.write()
    
    if lcdString1 != displayedString1:
        lcd.move_to(0, 0)
        lcd.putstr(lcdString1)
        displayedString1 = lcdString1
    if lcdString2 != displayedString2:
        lcd.move_to(0, 1)
        lcd.putstr(lcdString2)
        displayedString2 = lcdString2
    
    
    time.sleep(2)