# -*- coding: utf-8 -*-
import requests, datetime, base64, pymysql, time, re, datetime

###### CONFIGURATION PYTHON SCRIPT ######

# get it here: https://voe.sx/?op=my_account
voe_api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

# Embed or Direct Link format? (1 or 0)
embed = 1

# MySQL Database
database_username = 'USERNAME'
database_password = 'PASSWORD'
database_host = '127.0.0.1'
database_database = 'DATABASE_NAME'

# Table name in which the links are located
database_table = 'wp_postmeta'

##########################################
# (ignore these settings)

# to avoid overloading / IP blocking
sleep_seconds_after_web_request = 0.15
sleep_seconds_after_database_request = 0.15

# Database maximal updates per link / limits the damage in case of errors
database_max_updates_per_link = 30

###########

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
}

db = pymysql.connect(host=database_host, user=database_username, passwd=database_password, db=database_database)
cur = db.cursor()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def isDateTimeInFuture(server_date_time, delete_date_time):
    now = datetime.datetime.strptime(server_date_time, "%Y-%m-%d %H:%M:%S")
    parsed_date_time = datetime.datetime.strptime(delete_date_time, "%Y-%m-%d %H:%M:%S")
    if(parsed_date_time>=now):
        return True
    else:
        print(bcolors.WARNING + '- ' + delete_date_time + ' is in the past. The file has already been removed.' + bcolors.ENDC)
        return False

def checkIfOldLinkStillInUse(old_link):
    if not re.search(r"^(https?:\/\/)?(www\.)?voe\.sx(\/e\/|\/)([A-Za-z0-9]{12})$", old_link):
        print(bcolors.FAIL + ' - error: new link invalid ' + old_link + bcolors.ENDC)
        return False

    cur.execute('select count(*) as counter from ' + database_database + '.' + database_table + ' WHERE INSTR(meta_value, "' + old_link + '") > 0 LIMIT 1;')
    time.sleep(sleep_seconds_after_database_request)

    link_counter = cur.fetchone()
    if not link_counter:
        print(bcolors.WARNING + ' - info: link no longer in database or has already been replaced: ' + old_link + bcolors.ENDC)
        return False
    if int(link_counter[0] > 0):
        return True
    else:
        print(bcolors.WARNING + ' - info: link no longer in database or has already been replaced: ' + old_link + bcolors.ENDC)
        return False

def getVOEDMCAList():
    print('- get VOE Deleted/DMCA List')
    r = requests.get(
        'https://voe.sx/api/dmca/list?key=' + voe_api_key + '&last=last',
        headers=headers
    )
    time.sleep(sleep_seconds_after_web_request)
    content = r.json()
    if content:
        return content
    else:
        return False

def cloneVOELink(file_code):
    print(' - clone VOE code ' + file_code)

    if not re.search(r'^([A-Za-z0-9]{12})$', file_code):
        print(bcolors.FAIL + ' - error: old link code invalid ' + file_code + bcolors.ENDC)
        return False

    r = requests.get(
        'https://voe.sx/api/file/clone?key=' + voe_api_key + '&file_code=' + file_code,
        headers=headers
    )
    time.sleep(sleep_seconds_after_web_request)
    content = r.json()

    if not re.search(r'^([A-Za-z0-9]{12})$', content['result']['filecode']):
        print(bcolors.FAIL + ' - error: new link code invalid ' + file_code + bcolors.ENDC)
        return False

    if content:
        return content['result']
    else:
        return False

def replaceOldLinkWithNewOne(old_link, new_link):
    print(' - replace VOE ' + old_link + ' with new one ' + new_link)

    if not re.search(r"^(https?:\/\/)?(www\.)?voe\.sx(\/e\/|\/)([A-Za-z0-9]{12})$", old_link):
        print(bcolors.FAIL + ' - error: old link code invalid ' + old_link + bcolors.ENDC)
        return False

    if not re.search(r"^(https?:\/\/)?(www\.)?voe\.sx(\/e\/|\/)([A-Za-z0-9]{12})$", new_link):
        print(bcolors.FAIL + ' - error: new link code invalid ' + new_link + bcolors.ENDC)
        return False

    cur.execute('UPDATE ' + database_database + '.' + database_table + ' SET meta_value = REPLACE(meta_value, "' + old_link + '", "' + new_link + '") WHERE INSTR(meta_value, "' + old_link + '") > 0 limit ' + str(database_max_updates_per_link) + ';')
    time.sleep(sleep_seconds_after_database_request)
    print(bcolors.OKGREEN + ' - Link has been successfully replaced. ' + bcolors.ENDC)

print(bcolors.OKBLUE + bcolors.BOLD + '# VOE Deleted Files/DMCA Replacement #' + bcolors.ENDC)
print('')

DMCA_result = getVOEDMCAList()
DMCA_links = DMCA_result['result']
server_time = DMCA_result['server_time']

if(DMCA_links):
    for DMCA_link in DMCA_links:
        print(' - process ' + DMCA_link['embed_url'])

        if not (isDateTimeInFuture(server_time, DMCA_link['del_time'])):
            print('')
            continue

        if not (checkIfOldLinkStillInUse(DMCA_link['embed_url'])):
            print('')
            continue

        new_link = cloneVOELink(DMCA_link['file_code'])
        if(new_link):
            if(embed):
                result = replaceOldLinkWithNewOne('https://voe.sx/e/' + DMCA_link['file_code'], 'https://voe.sx/e/' + new_link['filecode'])
            else:
                result = replaceOldLinkWithNewOne('https://voe.sx/' + DMCA_link['file_code'], 'https://voe.sx/' + new_link['filecode'])
        print('')
    print(bcolors.OKBLUE + bcolors.BOLD + '# completed, all reports processed. #' + bcolors.ENDC)
else:
    print('no DMCA Links found.')