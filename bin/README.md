# Configure Raspberry Pi

1. Format SD
2. Edit `wpa_sipplicant.conf` with WiFi info
3. Move `ssh` and `wpa_sipplicant.conf` to the boot partition on Pi
4. Install git on Pi
5. Install pip on Pi
6. Clone Repo
7. Install Deps
8. Set AdafruitIO keys to env
9. Test script
10. Add to crontab
11. Make python script executable

```sh
sudo apt update
sudo apt install git
git --version
```

```sh
git config --global user.name "HoukasaurusRex"
git config --global user.email "jt1992@gmail.com"
```

```sh
sudo apt install python3-pip
```

grep CRON /var/log/syslog --text

```crontab
@reboot cd ~/RaspberryPi-AQIPi && git pull -q origin master

# set path to python deps and run script on reboot
@reboot PYTHONPATH=/usr/lib/python3/dist-packages python3 /home/pi/RaspberryPiAQIPi/main.py &

# write logs to logs/aqipi.log
* * * * * /home/pi/RaspberryPi-AQIPi/main.py >> /home/pi/logs/aqipi.log 2>&1
```
