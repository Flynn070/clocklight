from machine import Pin, ADC, I2C
from ssd1306 import SSD1306_I2C
from neopixel import NeoPixel
import time, onewire, ds18x20

#turn on LED to indicate initiation
onboardLED = Pin(25, Pin.OUT)
onboardLED.value(1)

#assign pins
#28 - neopixel, 27 - light sensor, 26 - potentiometer, 20 - thermometer, 17 - OLED scl, 16, OLED sda
potentiometer = ADC(Pin(26))		#0-65535
lightSensor = ADC(Pin(27))			#0-65535
thermometerPin = Pin(20, Pin.IN)

thermometer = ds18x20.DS18X20(onewire.OneWire(thermometerPin))
thermometerRoms = thermometer.scan()

ledStrip = NeoPixel(Pin(28), 15)

i2c=I2C(0,sda=Pin(16), scl=Pin(17), freq=400000)
time.sleep(1)
#display = SSD1306_I2C(128, 32, i2c)	#is not workigngggggg
#display.fill(0)

currentTime = time.time()


onboardLED.value(0)
while True:
    print("pot - " + str(potentiometer.read_u16()))
    print("light - " + str(lightSensor.read_u16()))
    thermometer.convert_temp()
    for rom in thermometerRoms:
        print((thermometer.read_temp(rom)),"C")
    print("\n")
    ledStrip[0] = (255, 0, 0)
    ledStrip.write()
    time.sleep(1)
    ledStrip[0] = (0, 0, 0)
    ledStrip.write()
    time.sleep(10)