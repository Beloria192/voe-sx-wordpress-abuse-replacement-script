import json
import requests

# API Key - https://voe.sx/settings (Account -> API Details)
voe_api_key = ''

# MySQL Database Configuration
database_username = 'wordpress'
database_password = ''
database_host = 'localhost'
database_database = 'wordpress'

# MySQL tables & their field that should be checked.
#  the script looks up: voe.sx/e/(code) and voe.sx/(code) and i.voe.sx/cache/(code)_storyboard
replacements = [
    {'table': 'wp_posts', 'field': 'post_content'},
    {'table': 'wp_postmeta', 'field': 'meta_value'},
    # ...
]

# Database maximal updates per link / limits the damage in case of errors.
database_max_updates_per_link = 50

# MySQL Connection (equivalent to $mysqli = new mysqli(...))
import pymysql.cursors
connection = pymysql.connect(
    host=database_host,
    user=database_username,
    password=database_password,
    db=database_database,
    cursorclass=pymysql.cursors.DictCursor
)

def replace_old_link_with_new_one(old_link, new_link):
    global replacements, connection, database_max_updates_per_link
    print(f" - replace VOE {old_link} with new one {new_link}\n")

    with connection.cursor() as cursor:
        for replacement in replacements:
            query = f"UPDATE {replacement['table']} SET {replacement['field']} = REPLACE({replacement['field']}, %s, %s) WHERE INSTR({replacement['field']}, %s) > 0 LIMIT {database_max_updates_per_link}"
            cursor.execute(query, (old_link, new_link, old_link))

    connection.commit()
    print("- Link has been successfully replaced.\n")

print("# VOE Deleted Files/DMCA Replacement #\n")

print("- get VOE Deleted/DMCA List\n")
dmca_url = f"https://voe.sx/api/dmca/list?key={voe_api_key}&pending=true"
r = requests.get(dmca_url)
data = json.loads(r.text)

DMCA_links = data['result']
server_time = data['server_time']

if DMCA_links:
    for DMCA_link in DMCA_links:
        print(f" - process {DMCA_link['file_code']}\n")

        del_time = DMCA_link['del_time']
        file_code = DMCA_link['file_code']

        if del_time >= server_time:
            link_found = False

            with connection.cursor() as cursor:
                for replacement in replacements:
                    if link_found:
                        continue

                    query = f"SELECT COUNT(*) as counter FROM {replacement['table']} WHERE INSTR({replacement['field']}, %s) > 0 LIMIT 1"
                    cursor.execute(query, (file_code,))
                    row = cursor.fetchone()
                    if row['counter'] > 0:
                        link_found = True

            if link_found:
                print("\n - clone VOE code {file_code}\n")
                r = requests.get(f"https://voe.sx/api/file/clone?key={voe_api_key}&file_code={file_code}")
                data = json.loads(r.text)
                new_link = data['result']['filecode']

                replace_old_link_with_new_one(f"voe.sx/e/{file_code}", f"voe.sx/e/{new_link}")
                replace_old_link_with_new_one(f"voe.sx/{file_code}", f"voe.sx/{new_link}")
                replace_old_link_with_new_one(f"i.voe.sx/cache/{file_code}_storyboard", f"i.voe.sx/cache/{new_link}_storyboard")
                print("\n")
            else:
                print("\n")
        else:
            print("\n")
    print("# completed, all reports processed. #\n")
else:
    print("No DMCA Links found.\n")

connection.close()