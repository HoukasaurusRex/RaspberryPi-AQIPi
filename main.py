#!/usr/bin/env python3

from os import getenv
from time import sleep
from datetime import datetime
from statistics import median
from dotenv import load_dotenv
from serial import Serial, serialutil
from Adafruit_IO import Client
import random

load_dotenv()
AIO_USERNAME = getenv('AIO_USERNAME')
AIO_KEY = getenv('AIO_KEY')
CITY = getenv('CITY')
AIO_LOGS = getenv('AIO_LOGS')

aio = Client(AIO_USERNAME, AIO_KEY)
error_count = 0
retry_count = getenv('RETRY_COUNT') or 15
ser = Serial()
usb_ports = [
  '/dev/ttyUSB0',
  '/dev/cu.usbserial-1410', # Mac serial port `ls -lha /dev/cu.usbserial-*`
  '/dev/cu.usbserial-1420',
  '/dev/cu.usbserial-1430',
  '/dev/cu.usbserial-1440'
]

def get_time():
  format = '%Y-%m-%d %H:%M:%S'
  now = datetime.now()
  return now.strftime(format)

def log(msg):
  msg_payload = f'{get_time()}: {msg}'
  print(msg_payload)
  if AIO_LOGS:
    try:
      aio.send(AIO_LOGS, msg_payload)
    except Exception as error:
      print('Error submitting logs to aio: ', error)
      print('Original message: ', msg_payload)

for i, port in enumerate(usb_ports):
  try:
    ser = Serial(port)
    log(f'Reading from {port}')
    break
  except serialutil.SerialException as serial_error:
    if i >= len(usb_ports):
      log(serial_error)
      raise serial_error
    continue
  except Exception as error:
    log(error)
    raise error

def find_bp(bp_name, data):
  aqi_bp = [0, 50, 100, 150, 200, 300, 400, 500]
  pm_twofive_cb = [0.0, 12.0, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4]
  pm_ten_cb = [0, 54, 154, 254, 354, 424, 504, 604]
  breakpoints = pm_twofive_cb if bp_name == 'pm_twofive' else pm_ten_cb
  bp_index = 0
  high = breakpoints[bp_index]
  while high < data:
    bp_index += 1
    if bp_index >= len(breakpoints) and high < data:
      raise ValueError(f'Measured value in {bp_name} exceeded index range. Expected value not to exceed {high}, but received {data}. This is most likely an issue with the connected sensor, unless you\'re having a very bad AQI day') 
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
  return int(round(I))

def send_data(name, data):
  aio.send(f'{CITY}-{name}', data)

def read_data():
  pm_twofive_data = []
  pm_ten_data = []
  readings = 0
  while readings < 11:
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
  send_data('twofive', pm_twofive_aqi)
  pm_ten_aqi = calc_aqi('pm_ten', median(pm_ten_data))
  send_data('ten', pm_ten_aqi)
  return [pm_twofive_aqi, pm_ten_aqi]

def retry_connection(timeout):
  ser.close()
  sleep(timeout)
  ser.open()

def exponential_backoff(n):
  return (2 ** n) + (random.randint(0, 1000) / 1000)

def handle_error(error):
  global error_count
  if error_count > retry_count:
    raise error
  error_count += 1
  backoff_time = exponential_backoff(error_count)
  log(f'{error} \n Retrying in {backoff_time} seconds...')
  retry_connection(backoff_time)
  log('Reconnected')

def run():
  log('Starting AQI Monitor script')
  while True:
    try:
      global error_count
      read_data()
      error_count = 0
    except Exception as error:
      handle_error(error)
    finally:
      sleep(1)

try:
  run()
except Exception as error:
  log(error)
  raise error