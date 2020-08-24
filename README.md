# RaspberryPi-AQIPi

Collects air quality data from the SDS011 sensor and pushes it to Adafruit IO

## Prerequisites

- SDS011 Air Quality Sensor
- Raspberry Pi (Configured with Raspbian or similar Linux-based OS)
- Python3
- AdafruitIO account (Or similar dashboard to push and monitor results)

## Getting Started

Connect the SDS011 to the Raspberry Pi with the serial adapter, install the project dependencies, then run `main.py`.
Once the code is running fine, add the script to your `crontab`.

### Setting Env Vars

```sh
export AIO_USERNAME='MyAIOUsername'
export AIO_KEY='MyAIOActiveKey'
export CITY='beijing'
```

### Installing Globally

```sh
pip3 install -r requirements.txt
python3 main.py
```

### Installing Locally

```sh
pipenv install -e
pipenv run main.py
```

### Add to Crontab

```sh
crontab -e
```

and add

```sh
# set path to python deps and run script on reboot
@reboot PYTHONPATH=/usr/lib/python3/dist-packages python3 /home/pi/RaspberryPiAQIPi/main.py &

# write logs to logs/aqipi.log
* * * * * /home/pi/RaspberryPi-AQIPi/main.py >> /home/pi/logs/aqipi.log 2>&1
```

### Make it Executable

```sh
chmod u+x /home/pi/RaspberryPi-AQIPi/main.py
```

## Safe levels

Once you’re monitoring your PM2.5 data, what should you look out for? The World Health Organisation air quality guideline stipulates that PM2.5 not exceed 10 µg/m3 annual mean, or 25 µg/m3 24-hour mean; and that PM10 not exceed 20 µg/m3 annual mean, or 50 µg/m3 24-hour mean. However, even these might not be safe. In 2013, a large survey published in The Lancet “found a 7% increase in mortality with each 5 micrograms per cubic metre increase in particulate matter with a diameter of 2.5 micrometres (PM2.5).”

## Where to locate your sensor

Standard advice for locating your sensor is that it should be outside and four metres above ground level. That’s good advice for general environmental monitoring; however, we’re not necessarily interested in general environmental monitoring – we’re interested in knowing what we’re breathing in.

Locating your monitor near your workbench will give you an idea of what you’re actually inhaling – useless for any environmental study, but useful if you spend a lot of time in there. We found, for example, that the glue gun produced huge amounts of PM2.5, and we’ll be far more careful with ventilation when using this tool in the future.

## Acknowledgements

- Andrew Gregory from [raspberrypi.org](https://www.raspberrypi.org/blog/monitor-air-quality-with-a-raspberry-pi/)