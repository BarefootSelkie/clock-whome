import time
import machine
import badger2040
from pngdec import PNG

### Constants ###

summerTime = True

# Time constants for headspace
hsTick = 1 # done like this to allow for future adding for smaller units
hsFractalLen = hsTick * 6
hsMinorLen = hsFractalLen * 6
hsMajorLen = hsMinorLen * 6
hsSeasonLen = hsMajorLen * 6
hsCycleLen = hsSeasonLen * 6

rsLetterSpacing = 2
hsLetterSpacing = 1
hsSpaceWidth = 8

### Initialisation

display = badger2040.Badger2040()
display.set_update_speed(0)
display.set_thickness(4)

WIDTH, HEIGHT = display.get_bounds()
CENTRE = (badger2040.WIDTH / 2)

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
    hsTimeObject[1] = int(remainder // hsSeasonLen)
    remainder = ticks % hsSeasonLen
    hsTimeObject[2] = int(remainder // hsMajorLen)
    remainder = ticks % hsMajorLen
    hsTimeObject[3] = int(remainder // hsMinorLen)
    remainder = ticks % hsMinorLen
    hsTimeObject[4] = int(remainder // hsFractalLen)
    remainder = ticks % hsFractalLen
    hsTimeObject[5] = int(remainder // hsTick)

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

    # Initialise PNG renderer
    png = PNG(display.display)

    # Draw Heaspace time / date
    # Create a sting holding the current day of season in base 10
    dayString = str(((hsTimeNow(zeropoint)[2]) * 6) + hsTimeNow(zeropoint)[3] + 1)
    totalWidth = 0

    # Measure all the things to display
    png.open_file("/clock-hs/fractals28px/" + str(hsTimeNow(zeropoint)[4]) + ".png")
    totalWidth = totalWidth + png.get_width() + hsLetterSpacing
    png.open_file("/clock-hs/ticks28px/" + str(hsTimeNow(zeropoint)[5]) + ".png")
    totalWidth = totalWidth + png.get_width() + hsSpaceWidth
    png.open_file("/clock-hs/numerals28px/" + dayString[0] + ".png")
    totalWidth = totalWidth + png.get_width() + hsSpaceWidth
    if len(dayString) > 1:
        png.open_file("/clock-hs/numerals28px/" + dayString[1] + ".png")
        totalWidth = totalWidth + png.get_width() + hsLetterSpacing
    png.open_file("/clock-hs/seasonNames28px/" + str(hsTimeNow(zeropoint)[1]) + ".png")
    totalWidth = totalWidth + png.get_width() + hsSpaceWidth
    png.open_file("/clock-hs/seasons28px/" + str(hsTimeNow(zeropoint)[1]) + ".png")
    totalWidth = totalWidth + png.get_width()

    # Work out where to start drawing if everything is centred
    hsStart = int(CENTRE - (totalWidth / 2))

    # Draw the images and text for the headspace time/date
    cursor = hsStart

    png.open_file("/clock-hs/fractals28px/" + str(hsTimeNow(zeropoint)[4]) + ".png")
    png.decode(cursor, 96)
    cursor = cursor + png.get_width() + hsLetterSpacing

    png.open_file("/clock-hs/ticks28px/" + str(hsTimeNow(zeropoint)[5]) + ".png")
    png.decode(cursor, 96)
    cursor = cursor + png.get_width() + hsSpaceWidth

    png.open_file("/clock-hs/numerals28px/" + dayString[0] + ".png")
    png.decode(cursor, 96)
    cursor = cursor + png.get_width() 

    if len(dayString) > 1:
        png.open_file("/clock-hs/numerals28px/" + dayString[1] + ".png")
        png.decode(cursor, 96)
        cursor = cursor + hsLetterSpacing + png.get_width()
        
    cursor = cursor + hsSpaceWidth

    png.open_file("/clock-hs/seasonNames28px/" + str(hsTimeNow(zeropoint)[1]) + ".png")
    png.decode(cursor, 96)
    cursor = cursor + png.get_width() + hsSpaceWidth

    png.open_file("/clock-hs/seasons28px/" + str(hsTimeNow(zeropoint)[1]) + ".png")
    png.decode(cursor, 96)

    # Draw the meat space clock

    # draw a colon in the middle of the display
    png.open_file("/clock-hs/numerals96px/colon.png")
    colonWidth = png.get_width()
    colonLeft = int(CENTRE - (colonWidth / 2))
    png.decode(int(colonLeft), -10)

    # get the time in the correct format
    if not summerTime:
        timeString = "{:02}{:02}:".format(hour, minute)
    else:
        timeString = "{:02}{:02}:".format(((hour + 1) % 24), minute)

    # draw the minutes msb
    png.open_file("/clock-hs/numerals96px/" + str(timeString[2]) + ".png")
    minuteMSBWidth = png.get_width()
    minuteMSBLeft = colonLeft + colonWidth + rsLetterSpacing
    png.decode(int(minuteMSBLeft), 0)

    # draw the minutes lsb
    png.open_file("/clock-hs/numerals96px/" + str(timeString[3]) + ".png")
    minuteLSBWidth = png.get_width()
    minuteLSBLeft = minuteMSBLeft + minuteMSBWidth + rsLetterSpacing
    png.decode(int(minuteLSBLeft), 0)

    # draw the hour lsb
    png.open_file("/clock-hs/numerals96px/" + str(timeString[1]) + ".png")
    hourLSBWidth = png.get_width()
    hourLSBLeft = colonLeft - (rsLetterSpacing + hourLSBWidth)
    png.decode(int(hourLSBLeft), 0)

    # draw the hour msb
    png.open_file("/clock-hs/numerals96px/" + str(timeString[0]) + ".png")
    hourMSBWidth = png.get_width()
    hourMSBLeft = hourLSBLeft - (rsLetterSpacing + hourMSBWidth)
    png.decode(int(hourMSBLeft), 0)

    # send the image to the eink display hardward to display it on screen
    display.update()


year, month, date, wd, hour, minute, second, _ = rtc.datetime()

last_minute = minute
draw_clock()

while True:
    # Load RTC into variables
    year, month, date, wd, hour, minute, second, _ = rtc.datetime()

    if minute != last_minute:
        draw_clock()
        last_minute = minute

    time.sleep(1)
# mpremote
