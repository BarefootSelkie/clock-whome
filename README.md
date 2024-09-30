# Meat / Head Space Clock

This is used as the clock module to [home-info-display](https://github.com/BarefootSelkie/home-info-display) it uses a Badger2040W for it's fast updating clock to display the current meatspace time in 24 hours format. It also displays my head space time below it.

{the headspace clock needs to have an option to switch that off, as it's only useful to us -ry}

The [MicroPython command line tool](https://docs.micropython.org/en/latest/reference/mpremote.html) works about the best for copying code over to the rp2040, the [fs subcommands](https://docs.micropython.org/en/latest/reference/mpremote.html#mpremote-command-fs) are what we need for copying code.

To connect Badger2040W to a network you will need to edit the WIFI_CONFIG.py in the root folder - more details [on the Pimoroni page](https://learn.pimoroni.com/article/getting-started-with-badger-2040#customising-the-badgeros-examples).

zeropoint.txt contains the zero point in unix seconds

## Fonts

Fonts used for the real space clock are [Fredoka Variable Font](https://github.com/PanicKk/Fredoka-Font/) by [PanicKk](https://github.com/PanicKk)