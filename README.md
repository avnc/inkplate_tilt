# Inkplate5 & Tilt Hydrometer
This is a Micropython project to display [Tilt Hydrometer](https://tilthydrometer.com/products/copy-of-tilt-floating-wireless-hydrometer-and-thermometer-for-brewing) values on a [Soldered Inkplate 5](https://soldered.com/product/soldered-inkplate-5-gen2/). This code owes much to these two projects which worked out the hard bluetooth part of this equation: https://github.com/myoung34/bluey-lite and https://github.com/jicese/picoTilt and from which I have borrowed liberally.

The **Inkplate 5** is a cool little e-ink display with a built-in ESP32 microcontroller that can be programmed in Arduino or Micropython. I went with Micropython and to do the same, you'll need to follow the setup instructions for the board here: https://github.com/SolderedElectronics/Inkplate-micropython/tree/master. Note, Soldered includes a Micropython firmware to use based on Micropython 1.18 so it may be missing some newer Micropython features. It is possible to outfit it with later versions but this did not work well for me when I tried.

You'll also need to grab the default Inkplate driver files from the the Inkplate repo, I've only included my `main.py` file. You'll need these:
- `gfx.py`
- `gfx_standard_font_01.py`
- `inkplate5.py`
- `mcp23017.py`
- `PCAL6416A.py`
- `shapes.py`

The **Tilt Hydrometer** is a sensor that floats in your beer fermentation vessel and provides measurements of temperature and specific gravity. It's relatively simple to gather data from given a microcontroller with bluetooth support. I initially used a Pimoroni InkyFrame with a built-in Raspberry Pi Pico W, but went with this solution for a bit less clunky of a presence in my pantry (where my fermentation vessels sit). I have two of these, and they are identified by color (which is associated with a bluetooth UUID). If you have just a single Tilt it should be easy to modify the code accordingly.

## ToDo
Things to be improved on:
- make the tilt handling code a bit more generic (so it automatically handles one or two devices of any color)
- improve the power saving by implementing a deep sleep after reading values.
