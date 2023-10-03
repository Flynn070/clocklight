from machine import Pin, ADC, I2C
from neopixel import NeoPixel
import time, onewire, ds18x20

#turn on LED to indicate initiation
onboardLED = Pin(25, Pin.OUT)
onboardLED.value(1)

#assign pins
#28 - neopixel, 27 - light sensor, 26 - potentiometer, 20 - thermometer, 17 - OLED scl, 16, OLED sda
potentiometer = ADC(Pin(26))		#0-65535
lightSensor = ADC(Pin(27))
thermometerPin = Pin(20, Pin.IN)

thermometer = ds18x20.DS18X20(onewire.OneWire(thermometerPin))
thermometerRoms = thermometer.scan()

ledStrip = NeoPixel(Pin(28), 15)

i2c=I2C(0,sda=Pin(16), scl=Pin(17), freq=400000)
time.sleep(1)
display = SSD1306_I2C(128, 32, i2c)
display.fill(0)

currentTime = time.time()

while True:
    