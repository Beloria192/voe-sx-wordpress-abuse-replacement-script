<?php

// API Key - https://voe.sx/settings (Account -> API Details)
$voe_api_key = '';

// MySQL Database Configuration
$database_username = 'wordpress';
$database_password = '';
$database_host = 'localhost';
$database_database = 'wordpress';

// MySQL tables & their field that should be checked.
//  the script looks up: voe.sx/e/(code) and voe.sx/(code) and i.voe.sx/cache/(code)_storyboard
$replacements = [
    ['table' => 'wp_posts', 'field' => 'post_content'],
    ['table' => 'wp_postmeta', 'field' => 'meta_value'],
    // ...
];

// Database maximal updates per link / limits the damage in case of errors.
$database_max_updates_per_link = 50;

$mysqli = new mysqli($database_host, $database_username, $database_password, $database_database);
if ($mysqli->connect_errno) {
    die('Failed to connect to MySQL: ' . $mysqli->connect_error);
}

function replaceOldLinkWithNewOne($old_link, $new_link)
{
    global $replacements, $mysqli, $database_max_updates_per_link;
    echo " - replace VOE $old_link with new one $new_link" . "\r\n <br>";

    foreach ($replacements as $replacement) {
        $query = "UPDATE " . $replacement['table'] . " SET " . $replacement['field'] . " = REPLACE(" . $replacement['field'] . ", '$old_link', '$new_link') WHERE INSTR(" . $replacement['field'] . ", '$old_link') > 0 LIMIT $database_max_updates_per_link;";
        $mysqli->query($query);
    }
    echo "- Link has been successfully replaced." . "\r\n <br>";
}

echo "# VOE Deleted Files/DMCA Replacement #" . "\r\n <br>";
echo "\r\n <br>";

echo "- get VOE Deleted/DMCA List" . "\r\n <br>";
$dmca_url = "https://voe.sx/api/dmca/list?key=$voe_api_key&pending=true";
$r = file_get_contents($dmca_url);
$data = json_decode($r, true);

$DMCA_links = $data['result'];
$server_time = $data['server_time'];

if ($DMCA_links) {
    foreach ($DMCA_links as $DMCA_link) {
        echo " - process {$DMCA_link['file_code']}" . "\r\n <br>";

        $del_time = $DMCA_link['del_time'];
        $file_code = $DMCA_link['file_code'];

        if (strtotime($del_time) >= strtotime($server_time)) {
            $link_found = false;

            foreach ($replacements as $replacement) {
                if ($link_found) {
                    continue;
                }

                $cur = $mysqli->query("SELECT COUNT(*) as counter FROM " . $replacement['table'] . " WHERE INSTR(" . $replacement['field'] . ", '$file_code') > 0 LIMIT 1;");
                $row = $cur->fetch_assoc();
                if ($row['counter'] > 0) {
                    $link_found = true;
                }
            }

            if ($link_found) {
                echo "\r\n <br>";
                echo " - clone VOE code $file_code" . "\r\n <br>";
                $r = file_get_contents("https://voe.sx/api/file/clone?key=$voe_api_key&file_code=$file_code");
                $data = json_decode($r, true);
                $new_link = $data['result']['filecode'];

                replaceOldLinkWithNewOne("voe.sx/e/$file_code", "voe.sx/e/$new_link");
                replaceOldLinkWithNewOne("voe.sx/$file_code", "voe.sx/$new_link");
                replaceOldLinkWithNewOne('i.voe.sx/cache/' . $file_code . '_storyboard', 'i.voe.sx/cache/' . $new_link . '_storyboard');
                echo "\r\n <br>";
            } else {
                echo "\r\n <br>";
            }
        } else {
            echo "\r\n <br>";
        }
    }
    echo "# completed, all reports processed. #" . "\r\n <br>";
} else {
    echo "No DMCA Links found." . "\r\n <br>";
}

$mysqli->close();