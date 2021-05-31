#!/bin/sh
cd /root
apt update -y
apt install -y wget python3 python3-pip
pip3 install pymysql
wget https://github.com/Beloria192/voe-sx-wordpress-abuse-replacement-script/raw/main/voe-wordpress-replacement.py
chmod +x ./voe-wordpress-replacement.py
crontab -l | { cat; echo "15 */4 * * * /usr/bin/python3 /root/voe-wordpress-replacement.py >> /root/voe-wordpress-replacement.log 2>&1"; } | crontab -
echo 'completed. Now please edit file nano ./voe-wordpress-replacement.py with your database settings / voe.sx api key'