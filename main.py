import os, serial, time
from Adafruit_IO import Client
from dotenv import load_dotenv

load_dotenv()
AIO_USERNAME = os.getenv("AIO_USERNAME")
AIO_KEY = os.getenv("AIO_KEY")
CITY = os.getenv('CITY')

aio = Client(AIO_USERNAME, AIO_KEY)
ser = serial.Serial('/dev/ttyUSB0')

while True:
    data = []
    for index in range(0, 10):
      datum = ser.read()
      data.append(datum)

    # `from_bytes` takes a string of bytes to convert to an int
    # since we have a list of two bytes instead of a single string,
    # we need to use `b''` to create an empty string of bytes
    # then `join` the bytes into it.
    # We divide the result by ten, because the SDS011 
    # returns data in units of tens of grams per metre cubed and we 
    # want the result in that format aio.send is used to push data to Adafruit IO
    pm_twofive = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
    aio.send(f'{CITY}-twofive', pm_twofive)
    pm_ten = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
    aio.send(f'{CITY}-ten', pm_ten)
    time.sleep(10)