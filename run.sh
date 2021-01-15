logfile="$(date +"%Y-%m-%d-%T")-aqipi.log"
touch "logs/$logfile"
(python3 main.py) > "logs/$logfile"