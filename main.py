#!/usr/bin/env python3

import serial
from os import getenv
from time import sleep
from datetime import datetime
from statistics import median
from dotenv import load_dotenv
from Adafruit_IO import Client

print(datetime.utcnow(), 'Starting AQI Monitor script')

load_dotenv()
AIO_USERNAME = getenv("AIO_USERNAME")
AIO_KEY = getenv("AIO_KEY")
CITY = getenv('CITY')

aio = Client(AIO_USERNAME, AIO_KEY)
ser = serial.Serial('/dev/ttyUSB0')
# ser = Serial('/dev/cu.usbserial-1410') # Mac serial port


def find_bp(bp_name, data):
  aqi_bp = [0, 50, 100, 150, 200, 300, 400, 500]
  pm_twofive_cb = [0.0, 12.0, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4]
  pm_ten_cb = [0, 54, 154, 254, 354, 424, 504, 604]
  breakpoints = pm_twofive_cb if bp_name == 'pm_twofive' else pm_ten_cb
  bp_index = 0
  high = breakpoints[bp_index]
  while high < data:
    bp_index += 1
    if high >= len(breakpoints) and high < data:
      raise ValueError(f'Measured value in {bp_name} exceeded index range. Expected value not to exceed {high}, but received {data}') 
    high = breakpoints[bp_index]

  return [breakpoints[bp_index - 1], breakpoints[bp_index], aqi_bp[bp_index - 1], aqi_bp[bp_index]]

def calc_aqi(name, data):
  bp = find_bp(name, data)
  C_low = bp[0]
  C_high = bp[1]
  C = data
  I_low = bp[2]
  I_high = bp[3]
  I = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low
  return I

def send_data(name, data):
  aio.send(f'{CITY}-{name}', data)

def read_data():
  pm_twofive_data = []
  pm_ten_data = []
  readings = 0
  while readings < 10:
    data = []
    for index in range(0, 10):
      datum = ser.read()
      data.append(datum)

    pm_twofive = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
    pm_twofive_data.append(pm_twofive)
    pm_ten = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
    pm_ten_data.append(pm_ten)
    readings += 1
    sleep(1)
  
  pm_twofive_aqi = calc_aqi('pm_twofive', median(pm_twofive_data))
  send_data('twofive', int(round(pm_twofive_aqi)))
  pm_ten_aqi = calc_aqi('pm_ten', median(pm_ten_data))
  send_data('ten', int(round(pm_ten_aqi)))

while True:
  try:
    read_data()
  except ValueError as error:
    print(datetime.utcnow(), error)
  except serial.serialutil.SerialException as serial_error:
    print(datetime.utcnow(), serial_error)