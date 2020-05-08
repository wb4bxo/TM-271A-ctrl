# PythonControl for TM-271a and TM-281A

This is a quick and dirty python script to control the Kenwood TM-271a and TM-281A for remote base type of uses.

The primary target for this is the Raspberry Pi but it has been tested and run mostly on Windows and Ubuntu as well.
This program targets Python 3, it has not been attempted to make it Python 2 compatible.
To run this script you will need to pip install pyserial.

Arguments passed in can be:

- ser xxx

  Where xxx is the name for the serial port appropriate for the OS.
  For example "ser COM3" for Windows or "ser /dev/tty0" for linux.
  NOTE - must be first argument if used. Environment variable
  "TM271Aser" is read if it exists as the default port to use.
- mem xxx

  Where xxx is up to a 3 digit memory number
- vfo xxxxxxxxxx{-|+}

  Where xxxxxxxxxx is the 10 digit frequency in Hz.
  The optional + or - sets the offset
- tone {x}xx.x

  Where {x}xx.x is a 2 or 3 digit whole number followed by a decimal.
  For example tone 141.3
  Note these must match exactly the standard tones
- ctcss {x}xx.x

  Where {x}xx.x is a 2 or 3 digit whole number followed by a decimal.
  For example tone 141.3
  Note these must match exactly the standard tones

- pow [h|l]

  Set transmit power to high or low (h or l)

Multiple arguments can be passed but may not make much sense except in
  the case of vfo and tone.
