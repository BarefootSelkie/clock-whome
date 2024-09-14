import time
import machine
import badger2040
from pngdec import PNG

letterSpacing = 2

display = badger2040.Badger2040()
display.set_update_speed(0)
display.set_thickness(4)

WIDTH, HEIGHT = display.get_bounds()

if badger2040.is_wireless():
    import ntptime
    try:
        display.connect()
        if display.isconnected():
            ntptime.settime()
    except (RuntimeError, OSError) as e:
        print(f"Wireless Error: {e.value}")
else:
    machine.reset()

# Thonny overwrites the Pico RTC so re-sync from the physical RTC if we can
try:
    badger2040.pcf_to_pico_rtc()
except RuntimeError:
    pass

rtc = machine.RTC()

display.set_font("sans")

button_a = badger2040.BUTTONS[badger2040.BUTTON_A]
button_b = badger2040.BUTTONS[badger2040.BUTTON_B]
button_c = badger2040.BUTTONS[badger2040.BUTTON_C]

button_up = badger2040.BUTTONS[badger2040.BUTTON_UP]
button_down = badger2040.BUTTONS[badger2040.BUTTON_DOWN]

# Button handling function
def button(pin):
    global year, month, day, hour, minute

    time.sleep(0.01)
    if not pin.value():
        return

    if button_a.value() and button_c.value():
        machine.reset()

def draw_clock():

    # Clear the display
    display.set_pen(15)
    display.clear()
    display.set_pen(0)

    # Draw the new information on the screen
    png = PNG(display.display)

    center = (badger2040.WIDTH / 2)
    png.open_file("/clock-hs/numerals/colon.png")
    colonWidth = png.get_width()
    colonLeft = center - (colonWidth / 2)
    png.decode(int(colonLeft), -10)

    timeString = "{:02}{:02}:".format(hour, minute)

    png.open_file("/clock-hs/numerals/" + str(timeString[2]) + ".png")
    minuteMSBWidth = png.get_width()
    minuteMSBLeft = colonLeft + colonWidth + letterSpacing
    png.decode(int(minuteMSBLeft), 0)

    png.open_file("/clock-hs/numerals/" + str(timeString[3]) + ".png")
    minuteLSBWidth = png.get_width()
    minuteLSBLeft = minuteMSBLeft + minuteMSBWidth + letterSpacing
    png.decode(int(minuteLSBLeft), 0)

    png.open_file("/clock-hs/numerals/" + str(timeString[1]) + ".png")
    hourLSBWidth = png.get_width()
    hourLSBLeft = colonLeft - (letterSpacing + hourLSBWidth)
    png.decode(int(hourLSBLeft), 0)

    png.open_file("/clock-hs/numerals/" + str(timeString[0]) + ".png")
    hourMSBWidth = png.get_width()
    hourMSBLeft = hourLSBLeft - (letterSpacing + hourMSBWidth)
    png.decode(int(hourMSBLeft), 0)

    #display.text(timeString, time_offset, 80, 0, 2.5)

    display.update()

for b in badger2040.BUTTONS.values():
    b.irq(trigger=machine.Pin.IRQ_RISING, handler=button)

year, month, date, wd, hour, minute, second, _ = rtc.datetime()
# Handle BST time zone
hour = hour + 1

last_minute = minute
draw_clock()

while True:
    # Load RTC into variables
    year, month, date, wd, hour, minute, second, _ = rtc.datetime()
    
    # Handle BST time zone
    hour = hour + 1

    if minute != last_minute:
        draw_clock()
        last_minute = minute
    
    time.sleep(1)
# mpremote
