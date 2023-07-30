# Voe.sx MySQL Website Reupload Script/Bot
###### For simple WordPress blogs & websites that use PHP or Python with MySQL as a database.
This script (available in both Python and PHP) automatically checks for broken or deleted links using the API.
If a URL is found to be broken, the script will automatically replace/clone it.

## How it Works
1. Retrieve all abused links using the voe.sx API.
2. Identify files scheduled for deletion in the future.
3. Check if these links still exist in your local MySQL database.
4. Clone the deleted link via API and replace the old URL code with a new one.

**Note**: Cached versions of your website may still display the old URLs due to cache plugins (WP Rocket, LiteSpeed Cache,  ...).

# PHP Version Installation (simple)
1. Download the '**voe-replacement.php**' file
2. Upload the '**voe-replacement.php**' file to your website (e.g. to a subfolder)
3. Adjust the configuration settings (database details, table, or column) in the script
4. Run the script by opening the website path, for example: **my-blog.net/tools/voe-replacement.php**
5. Create a Linux **cron job** or similar to run the script every few hours. This ensures regular checks and updates.
   e.g. 15 */2 * * * curl -s my-blog.net/tools/voe-replacement.php > /dev/null

# Python Version Installation (expert)
Run all commands below, sudo permission required:
1. cd /root
2. apt update -y
3. apt install -y wget python3 python3-pip
4. pip3 install pymysql
5. wget https://github.com/Beloria192/voe-sx-wordpress-abuse-replacement-script/raw/main/voe-replacement.py
6. chmod +x ./voe-wordpress-replacement.py
7. crontab -l | { cat; echo "15 */3 * * * /usr/bin/python3 /root/voe-wordpress-replacement.py >> /root/voe-wordpress-replacement.log 2>&1"; } | crontab -

Now the script automatically goes through the database every 3 hours at 15 after. Please test it once manually: python3 /root/voe-wordpress-replacement.py