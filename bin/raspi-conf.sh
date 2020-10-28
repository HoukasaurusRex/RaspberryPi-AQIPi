#!/bin/sh

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cp $DIR/raspi-conf/ssh /Volumes/boot/

envsubst < $DIR/raspi-conf/wpa_supplicant.conf > /Volumes/boot/wpa_supplicant.conf