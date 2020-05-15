# PythonControl for TM-271a and TM-281A

This is a quick and dirty python script to control the Kenwood TM-271a and TM-281A for remote base types of uses. It has been tested on both the TM-271A and TM-281A.

The primary target for this is the Raspberry Pi but it has been tested and runs on Windows and Ubuntu as well.
This program targets Python 3, it has not been attempted to make it Python 2 compatible.
To run this script you will need to pip install pyserial.
To install on HAMVOIP, which appears to have python3 but not pip3, I had to install pip3 as directed here: <https://pip.pypa.io/en/stable/installing/>

Arguments passed in can be:

- ser xxx

  Where xxx is the name for the serial port appropriate for the OS.
  For example "ser COM3" for Windows or "ser /dev/tty0" for linux.
  NOTE - must be first argument if used. Environment variable
  "TM271Aser" or "TM281Aser" is read if it exists as the default port to use.
- mem xxx

  Where xxx is up to a 3 digit memory number
- vfo xxxxxxxxxx{-|+}

  Where xxxxxxxxxx is the 10 digit frequency in Hz.
  If the leading character is not "1" a zero is appended as the GHz value.
  If 10 digits is not supplied, "0"s are appended to the end to 13 digits.
  Thus you can enter 0147330000 or 14733 for the same thing.
  The optional + or - sets the offset.
  This command clears any tone setting, set desired tone afterwards.
- tone {x}xx.x

  Where {x}xx.x is a 2 or 3 digit whole number followed by a decimal.
  For example tone 141.3.
  Note these must match exactly the standard tones.
  If tone freq is "0", the tone setting will be cleared.
- ctcss {x}xx.x

  Where {x}xx.x is a 2 or 3 digit whole number followed by a decimal.
  For example tone 141.3
  Note these must match exactly the standard tones

- pow [h|l]

  Set transmit power to high or low (h or l)

- freq

    Read frequency from display suitable for use with TTS.

    
Multiple arguments can be passed like "mem 33 freq" to change to a memory
and read back what the frequency is. Or "vfo 147330+ tone 100.0".
