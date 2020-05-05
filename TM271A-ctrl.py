#!/usr/bin/env python
import sys
import os
import time
import serial

# This is a quick and dirty control program for the Kenwood TM-271A and TM-281A
# transceiver to allow remote base like operations for use with Allstar or
# other digital modes. It is primarily targeted at the Raspberry Pi but being
# in Python allows it to be built and run on multiple platforms including
# Windows and Linux.
#
# This is targeting Python3 and you must install the pyserial libraries by
# issuing "pip3 install pyserial"

### Some global variables most for configuration and operation modes
usage = """
Arguments passed in can be:
  ser xxx
    Where xxx is the name for the serial port appropriate for the OS.
    For example "ser COM3" for Windows or "ser /dev/tty0" for linux.
    NOTE - must be first argument if used. Environment variable
    "TM271Aser" is read if it exists as the default port to use.
  mem xxx
    Where xxx is up to a 3 digit memory number
  vfo xxxxxxxxxx{-|+}
    Where xxxxxxxxxx is the 10 digit frequency in Hz.
    The optional + or - sets the offset
  tone {x}xx.x
    Where {x}xx.x is a 2 or 3 digit whole number followed by a decimal.
    For example tone 141.3 
    Note these must match exactly the standard tones
  ctcss {x}xx.x
    Where {x}xx.x is a 2 or 3 digit whole number followed by a decimal.
    For example tone 141.3 
    Note these must match exactly the standard tones
Multiple arguments can be passed but may not make much sense except in 
  the case of vfo and tone.
"""
serialName=os.getenv("TM271Aser")
if serialName is None:
    serialName = "/dev/ttyUSB0"
verbose=0
CTCSS_Tones = { # dictionary for tone to control number for the radio
"67.0"  : "00", 
"69.3"  : "01", 
"71.9"  : "02", 
"74.4"  : "03", 
"77.0"  : "04", 
"79.7"  : "05", 
"82.5"  : "06", 
"85.4"  : "07", 
"88.5"  : "08", 
"91.5"  : "09", 
"94.8"  : "10", 
"97.4"  : "11", 
"100.0" : "12", 
"103.5" : "13", 
"107.2" : "14", 
"110.9" : "15", 
"114.8" : "16", 
"118.8" : "17", 
"123.0" : "18", 
"127.3" : "19", 
"131.8" : "20", 
"136.5" : "21",
"141.3" : "22",
"146.2" : "23",
"151.4" : "24",
"156.7" : "25",
"162.2" : "26",
"167.9" : "27",
"173.8" : "28",
"179.9" : "29",
"186.2" : "30",
"192.8" : "31",
"203.5" : "32",
"206.5" : "33",
"210.7" : "34",
"218.1" : "35",
"225.7" : "36",
"229.1" : "37",
"233.6" : "38",
"241.8" : "39",
"250.3" : "40",
"254.1" : "41"
}

### Some functions we'll use

# Send and check for same thing to echo, try to resync if needed.
def sendAndWait(data):
    cnt = 50
    while 1:
        if cnt == 0:
            return "ERR"
        cnt -= 1
        ser.read(1000)
        ser.write((data + "\r").encode())
        rtn = ser.readline().decode()
        if rtn[0:2] == data[0:2]:
            break
        # Sometimes the radio gets out of sync and will return ?, E or the tail of something else...
        # It has not taken the command if it doesn't echo it back.
        if verbose >= 2:
            print("Retrying - Sent: " + data + " Got: " + rtn)
        # time.sleep(0.25)
        ser.write(("\r").encode())
        ser.read(1000)   # force timeout to flush buffers
        ser.read(1000)   # force timeout to flush buffers
    if verbose >= 2:
        print(rtn)
    return rtn

# Select a memory channel. Should be 3 digits but will fix it up if not
def memorySelect(mem):
    data = "VM 1"
    sendAndWait(data)
    if len(mem) > 3:    # sanity check in case more digits passed in than radio can handled
        mem = mem[-3]
    while len(mem) < 3: # radio requires 3 digit memory numbers
        mem = "0" + mem
    data="MR " + mem
    sendAndWait(data)
    return

# Select and set the vfo frequency passed in as string.
# freq should be 10 digits as Hz. as in 0147330000
# An appended + or - is used to signify offset
# VF format: (spaces only to align with description, omit when sending to radio)
#    3        14   16    18      20   22    24  26  29  32  36       45     47
# VF 0147330000,   0,    0,      0,   1,    0,  0, 13, 13,056,00600000,0     ,0
#          freq,step,shift,reverse,Tone,CTCSS,DCS,ENC,DEC,DCS,Offset  ,Narrow,BeatShift
def vfoSelect(freq):
    data = "VM 0"
    sendAndWait(data)
    current = sendAndWait("VF")
    if current[-1] == "\r":
        current = current[0:-1]
    if freq[-1] == "-":
        shift = "2"
        freq=freq[0:-1]
    elif freq[-1] == "+":
        shift = "1"
        freq=freq[0:-1]
    else:
        shift = "0"
    if freq[0] != "0":
        freq = "0" + freq
    if len(freq) > 10:
        freq = freq[0:10]
    while len(freq) < 10:
        freq = freq + "0"
    data = current[0:3] + freq + current[13:16] + shift + current[17:]
    sendAndWait(data)
    return

# Set the tone parameters for the current VFO setting. Reads what is in the radio,
# makes the changes, then writes it back.
# VF format: (spaces only to align with description, omit when sending to radio)
#    3        14   16    18      20   22    24  26  29  32  36       45     47
# VF 0147330000,   0,    0,      0,   1,    0,  0, 13, 13,056,00600000,0     ,0
#          freq,step,shift,reverse,Tone,CTCSS,DCS,ENC,DEC,DCS,Offset  ,Narrow,BeatShift
def vfoTone(toneFreq, tx, rx):
    if rx == 1: #there can only be one
        tx = 0
    current = sendAndWait("VF")
    if current[-1] == "\r":
        current = current[0:-1]
    theToneNumber = CTCSS_Tones[toneFreq]   
    if verbose >= 2:
        print( "Tone set to: " + theToneNumber)
    data = current[0:20] +  str(tx) + "," + str(rx) + ",0," + theToneNumber + "," + theToneNumber + current[31:]
    if verbose >= 2:
        print("Setting: " + data)
    sendAndWait(data)
    return

# Initialize the serial port as global variable ser
def serialInit(serPort):
    ser = serial.Serial(
        port= serPort, #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        rtscts=False,
        timeout=0.100
    )
    time.sleep(0.5) # mostly needed on Windows to allow port to settle in background
    return ser

#### Start of exectution
i=1
ser = None
if (len(sys.argv) > 1):
    if (sys.argv[i].lower() == "ser"):
        ser = serialInit(sys.argv[i+1])
        i += 2
    else:
        ser = serialInit(serialName)
    sendAndWait("AE")
# serial init must happen first
while i < len(sys.argv):
    if sys.argv[i].lower() == "mem":
        memorySelect(sys.argv[i+1])
        i += 2
    elif sys.argv[i].lower() == "vfo":
        vfoSelect(sys.argv[i+1])
        i += 2
    elif sys.argv[i].lower() == "tone":
        vfoTone(sys.argv[i+1], 1, 0)
        i += 2
    elif sys.argv[i].lower() == "ctcss":
        vfoTone(sys.argv[i+1], 0, 1)
        i += 2
    elif (sys.argv[i].lower())[0:2] == "-v":
        verbose = len(sys.argv[i]) - 1
        i += 1
        print ("Verbose: " + str(verbose))
    elif sys.argv[i].lower() == "help":
        print(usage)
        break
    else:
        print ("Error input:" + sys.argv[i])
        break
    # while

if ser is not None:
    ser.close()
