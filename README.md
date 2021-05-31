# Voe.sx WordPress Abuse Replacement Script
The Python script checks for broken or deleted links every 4 hours via the VOE.SX API. If a URL is broken, the URL will be replaced automatically.

## Procedure
- Get all deleted files via VOE API
- Check which files will be deleted in the future and have not yet been deleted
- Check if the links are still present in the local MySQL database
- Clone the deleted link via API and replace the old url code with a new url code
- The links have been successfully replaced

Please note that the old URLs may be displayed due to a cache plugin.

## Ubuntu/Debian Environment Requirements
- Python 3 (check with python3 -v if it was installed and install it with apt-get install python3 -y if it is not shown)
- Pip3 (apt install python3-pip)
- Python package pymysql (pip3 install pymysql)

## Manual execution
- /usr/bin/python3 ./voe-wordpress-replacement.py

## Cronjob “At minute 15 past every 4th hour.”
- crontab -e
- 15 */4 * * * /usr/bin/python3 /root/voe-wordpress-replacement.py >> /root/voe-wordpress-replacement.log 2>&1
