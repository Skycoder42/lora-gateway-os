#!/bin/sh
# $1 gps spoofer
# $2 tty path
# $3 latitude
# $4 longitude
# $5 altitude
set -x

# setup env vars
GPS_SPOOFER=${2:-"/opt/u-blox-pty/u-blox-pty.py"}
TTY_PATH=${3:-"/tmp/ttyGPS"}
LATITUDE=${4:-0.0}
LONGITUDE=${5:-0.0}
ALTITUDE=${6:-0}

# start the GPS spoofer
exec $GPS_SPOOFER "$TTY_PATH" $LATITUDE $LONGITUDE $ALTITUDE &
