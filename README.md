# Voe.sx WordPress Abuse Replacement Script
The Python script checks for broken or deleted links every 4 hours via the VOE.SX API. If a URL is broken, the URL will be replaced automatically.

## Procedure
- Get all deleted files via VOE API
- Check which files will be deleted in the future and have not yet been deleted
- Check if the links are still present in the local MySQL database
- Clone the deleted link via API and replace the old url code with a new url code
- The links have been successfully replaced

Please note that the old URLs may be displayed due to a cache plugin.

## Ubuntu/Debian Installation
- apt install wget;wget https://github.com/Beloria192/voe-sx-wordpress-abuse-replacement-script/raw/main/install.sh;chmod +x ./install.sh;./install.sh
- set your settings: nano ./voe-wordpress-replacement.py

## Manual execution
- /usr/bin/python3 ./voe-wordpress-replacement.py

## Cronjob “At minute 15 past every 4th hour.”
- crontab -e
- 15 */4 * * * /usr/bin/python3 /root/voe-wordpress-replacement.py >> /root/voe-wordpress-replacement.log 2>&1
- every 4 hours is enough, because the messages are usually announced 10 hours in advance.