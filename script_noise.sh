#!/bin/bash
sudo umount /media/Data2 
sudo umount /media/Data1
suco chmod 777 /dev/ttyS0
sudo chmod 777 /dev/ttyUSB*
sudo mkdir /media/Data1 
sudo mkdir /media/Data2
sudo mount /dev/sda6 /media/Data2 
sudo mount /dev/sda7 /media/Data1
#git stash
#git pull
#
python3 noise_measurement_system.py

