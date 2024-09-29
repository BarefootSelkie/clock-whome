import time
import machine
import badger2040
from pngdec import PNG

### Constants ###

# Time constants for headspace
hsTick = 1 # done like this to allow for future adding for smaller units
hsFractalLen = hsTick * 6
hsMinorLen = hsFractalLen * 6
hsMajorLen = hsMinorLen * 6
hsSeasonLen = hsMajorLen * 6
hsCycleLen = hsSeasonLen * 6

letterSpacing = 2

### Initialisation

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
            badger2040.pico_rtc_to_pcf()
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

# Get zeropoint from file

zeropointFile = "zeropoint.txt"
zeropointDefault = "946684800" # 2000-01-01 00:00

try: 
    stream = open(zeropointFile, "r")
except OSError:
    with open(zeropointFile, "w") as f:
        f.write(zeropointDefault)
        f.flush()
    stream = open(zeropointFile, "r")

# Read in the first line
zeropoint = int(stream.readline())

display.set_font("sans")

### Badger 2040 button handling ###

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

for b in badger2040.BUTTONS.values():
    b.irq(trigger=machine.Pin.IRQ_RISING, handler=button)



### Functions

# Converts an int of headspace ticks into a headspace date time object
# returns [cycles, seasons, weeks, days, fractals, ticks]
def hsTickTohsTimeObject(ticks):

    hsTimeObject = [0,0,0,0,0,0]
    # Time object is formatted Cycle, Season, Day Major, Day Minor, Fractal, Tick
    # + 1 added to lines for numbers that should not start counting at 0

    remainder = ticks
    hsTimeObject[0] = int(ticks // hsCycleLen)
    remainder = ticks % hsCycleLen
    hsTimeObject[1] = int(remainder // hsSeasonLen) + 1
    remainder = ticks % hsSeasonLen
    hsTimeObject[2] = int(remainder // hsMajorLen) + 1
    remainder = ticks % hsMajorLen
    hsTimeObject[3] = int(remainder // hsMinorLen) + 1
    remainder = ticks % hsMinorLen
    hsTimeObject[4] = int(remainder // hsFractalLen) + 1
    remainder = ticks % hsFractalLen
    hsTimeObject[5] = int(remainder // hsTick) + 1

    return(hsTimeObject)

# Takes in a period of time in seconds and converts it to a number of headspace ticks
# Designed to work with *datetime.total_seconds()*, returns an int
def rsSecondToTick(rsSeconds):
    return(rsSeconds // 400)

# Gets the current time in headspace based on zeropoint in zeropoint.txt
# returns: [cycles, seasons, day major, day minor, fractals, ticks]
def hsTimeNow(zeropoint):

    hsNowObj = hsTickTohsTimeObject(
        rsSecondToTick(
            time.time() - zeropoint
        )
    )

    return (hsNowObj)

def hsTimeTen(hsTimeObject):
  calcDays = (hsTimeObject[2] * 6) + hsTimeObject[3]
  return (f"{hsTimeObject[0]:d}-{hsTimeObject[1]:d}-{calcDays:d} {hsTimeObject[4]:d}:{hsTimeObject[5]:d}")

def draw_clock():

    # Clear the display
    display.set_pen(15)
    display.clear()
    display.set_pen(0)

    display.text(str(hsTimeTen(hsTimeNow(zeropoint))), 0, 113, 0, 1)

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

    display.update()


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
