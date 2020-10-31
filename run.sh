logfile="$(date +"%Y-%m-%d-%T")-aqipi.log"
touch $logfile
(python3 main.py) > "logs/$logfile" &