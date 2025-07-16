from machine import Pin

BCM, BOARD                 = 0, 1
OUT, IN                    = 0, 1
LOW, HIGH                  = 0, 1
PUD_DOWN, PUD_UP, PUD_NONE = 0, 1, -1

gpio = [ None ] * 30

def setwarnings(giveWarnings) : pass
def cleanup()                 : pass
def setmode(mode)             : pass

def setup(pin, mode, pullup=PUD_NONE):
    if   mode   == OUT      : gpio[pin] = Pin(pin, Pin.OUT)
    elif pullup == PUD_UP   : gpio[pin] = Pin(pin, Pin.IN, Pin.PULL_UP)
    elif pullup == PUD_DOWN : gpio[pin] = Pin(pin, Pin.IN, Pin.PULL_DOWN)
    else                    : gpio[pin] = Pin(pin, Pin.IN)
  
def output(pin, level):
    if level : gpio[pin].high()
    else     : gpio[pin].low()

def input(pin):
    return gpio[pin].value()