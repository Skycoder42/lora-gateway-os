#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# $1 expected tty path

import sys
import os
import os.path
import signal
import binascii
import struct
import time
import calendar
import math


### general helper stuff ###

latitude = 0
longitude = 0
altitude = 0

def write_padded(fd, data):
	if len(data) % 8 != 0:
		data = data + ("\0" * (len(data) % 8))
	os.write(fd, data)


### NMEA constants and methods ###

def nmea_checksum(data):
	checksum = 0
	for i in range(0, len(data), 1):
		checksum = checksum ^ struct.unpack("B", data[i])[0]
	return hex(checksum)[2:].upper()


def nmea_send(fd, cmd, args):
	nmea_args = [cmd]
	for arg in args:
		if arg is None:
			nmea_args.append("")
		else:
			nmea_args.append(str(arg))
	data = ",".join(nmea_args)
	write_padded(fd, "$" + data + "*" + nmea_checksum(data) + "\r\n")


def nmea_send_rmc(fd):
	nmea_args = [None] * 12  # NMEA sentence format: time, status, lat, NS, long, EW, spd, cog, date, mv, mvEW, posMode
	# date and time
	now = time.time()
	utc_now = time.gmtime(now)
	nmea_args[0] = "{:02d}{:02d}{:02d}".format(utc_now.tm_hour, utc_now.tm_min, utc_now.tm_sec) + "{:0.4f}".format(now % 1)[1:]
	nmea_args[8] = "{:02d}{:02d}{:02d}".format(utc_now.tm_mday, utc_now.tm_mon, utc_now.tm_year % 100)
	# gps status
	nmea_args[11] = "A"
	nmea_send(fd, "GPRMC", nmea_args)


def nmea_send_gga(fd):
	nmea_args = [None] * 14  # NMEA sentence format: time, lat, NS, long, EW, quality, numSV, HDOP, alt, M, sep, M, diffAge, diffStation
	# satelites
	nmea_args[6] = 3
	# GPS coordinates
	nmea_args[1] = "{:02d}{:0.10f}".format(int(abs(latitude)), (abs(latitude) % 1) * 60)
	nmea_args[2] = "N" if latitude >= 0 else "S"
	nmea_args[3] = "{:03d}{:0.10f}".format(int(abs(longitude)), (abs(longitude) % 1) * 60)
	nmea_args[4] = "E" if longitude >= 0 else "W"
	# altitude
	nmea_args[8] = altitude
	nmea_send(fd, "GPGGA", nmea_args)


### UBX constants and methods ###

ubx_sync1 = 0xb5
ubx_sync2 = 0x62

ubx_msg_class_cfg = 0x06
ubx_msg_id_cfg_msg = 0x01

ubx_msg_class_nav = 0x01
ubx_msg_id_nav_timegps = 0x20


def ubx_checksum(data):
	ck_a = 0
	ck_b = 0
	for i in range(0, len(data), 1):
		ck_a = ck_a + struct.unpack("B", data[i])[0]
		if ck_a > 255:
			ck_a = ck_a - 256
		ck_b = ck_b + ck_a
		if ck_b > 255:
			ck_b = ck_b - 256
	return ck_a, ck_b


def ubx_verify(data, cdata):
	bpack = struct.Struct("2B")
	ck_a_rcv, ck_b_rcv = bpack.unpack(cdata)
	ck_a, ck_b = ubx_checksum(data)
	return ck_a_rcv == ck_a and ck_b_rcv == ck_b


def ubx_send(fd, msg_class, msg_id, payload):
	header_pack = struct.Struct("< 4B H ")
	data = header_pack.pack(ubx_sync1, ubx_sync2, msg_class, msg_id, len(payload))
	data = data + payload

	checksum_pack = struct.Struct("2B")
	ck_a, ck_b = ubx_checksum(data[2:])
	data = data + checksum_pack.pack(ck_a, ck_b)
	write_padded(fd, data)


def ubx_send_time(fd):
	payload_pack = struct.Struct("< I i h 2B")

	# get times
	gps_epoche = calendar.timegm((1980, 1, 6, 0, 0, 0, 6, 1, -1))
	secs_per_week = 60 * 60 * 24 * 7
	now = time.time()
	# calculate weeks since gps epoche
	gps_week_frac, gps_week = math.modf((now - gps_epoche) / secs_per_week)
	# calculate i_tow, f_tow from gps_week_secs
	gps_week_ms = gps_week_frac * secs_per_week * 1000  # convert fraction to msecs of current week
	i_tow = round(gps_week_ms)  # milliseconds since begin of the week
	f_tow = round((gps_week_ms - i_tow) * 1000 * 1000)  # nanoseconds
	valid = 0x03
	payload = payload_pack.pack(i_tow, f_tow, gps_week, 0, valid)
	ubx_send(fd, ubx_msg_class_nav, ubx_msg_id_nav_timegps, payload)


def ubx_process_cmd(fd, msg_class, msg_id, payload):
	print hex(msg_class) + "-" + hex(msg_id) + ":", binascii.b2a_hex(payload)
	if msg_class == ubx_msg_class_cfg and msg_id == ubx_msg_id_cfg_msg:
		# send multiple time specs to init
		nmea_send_rmc(fd)
		time.sleep(1)
		ubx_send_time(fd)
		time.sleep(1)
		nmea_send_rmc(fd)
		time.sleep(1)
		ubx_send_time(fd)
		time.sleep(1)
		# start timesync loop
		while True:
			nmea_send_gga(fd)
			time.sleep(1)
			nmea_send_rmc(fd)
			time.sleep(1)
			ubx_send_time(fd)
			time.sleep(7)


def ubx_read(fd):
	header = os.read(fd, 4)
	header_pack = struct.Struct("< 2B H")
	msg_class, msg_id, payload_len = header_pack.unpack(header)

	payload = os.read(fd, payload_len)
	if ubx_verify(header + payload, os.read(fd, 2)):
		ubx_process_cmd(fd, msg_class, msg_id, payload)
	else:
		print "Invalid Checksum!"


### main loop and utility functions ###

def main(tty_path, set_latitude, set_longitude, set_altitude):
	global latitude
	global longitude
	global altitude
	latitude = float(set_latitude)
	longitude = float(set_longitude)
	altitude = int(set_altitude)

	master_fd, slave_fd = os.openpty()
	try:
		os.symlink(os.ttyname(slave_fd), tty_path)

		while True:
			sync_pack = struct.Struct("< 2B")
			sync1, sync2 = sync_pack.unpack(os.read(master_fd, 2))
			if sync1 == ubx_sync1 and sync2 == ubx_sync2:
				ubx_read(master_fd)
			else:
				print "Invalid message prefix: " + hex(sync1) + ", " + hex(sync2)
			sys.stdout.flush()
	finally:
		print "Exiting u-blox-pty..."
		os.close(slave_fd)
		os.close(master_fd)
		os.remove(tty_path)


def test(tty_path):
	master_fd, slave_fd = os.openpty()
	os.symlink(os.ttyname(slave_fd), tty_path)
	for i in range(0, 5, 1):
		time.sleep(5)
		ubx_send_time(master_fd)
	os.close(slave_fd)
	os.close(master_fd)
	os.remove(tty_path)


def sigexit_handler(_signo, _stack_frame):
	sys.exit(0)


### Entry point ###

if __name__ == "__main__":
	signal.signal(signal.SIGTERM, sigexit_handler)
	signal.signal(signal.SIGINT, sigexit_handler)
	main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	#test(sys.argv[1])
