import requests
import re
import yaml
import sys
import time
from requests.auth import HTTPBasicAuth

# url = "https://patch-diff.githubusercontent.com/raw/Harsh5006/ITDEV-Deployment/pull/33.diff"
url = sys.argv[1]


def extract_changed_files(diff_url):
    response = requests.get(diff_url)
    diff_text = response.text

    pattern = r'diff --git a/(.*?) b/\1'
    files_changed = re.findall(pattern, diff_text)

    return files_changed


changed_files = extract_changed_files(url)
for file in changed_files:
    print(file)


jenkins_url_east = 'http://172.208.35.136:8080/generic-webhook-trigger/invoke?token=742fre43g84'
jenkins_url_west = 'http://172.208.35.136:8080/generic-webhook-trigger/invoke?token=jsdue4v834b'

headers = {
    'Content-Type': 'application/json'
}



def trigger_jenkins_webhook(url, headers, payload):
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print('Jenkins job triggered successfully.')
    else:
        print(f'Failed to trigger Jenkins job. Status code: {response.status_code}')
        print('Response:', response.text)


for file in changed_files:
    with open(file) as f:
        data = yaml.safe_load(f)
    environment = 'production'
    application_id = data.get('application_id')
    version = data.get('version')
    testing_time = data.get('time_diff_regions_deployment')

    payload = {
            'parameter': [
                {'name': 'environment', 'value': environment },
                {'name': 'application_id', 'value': application_id},
                {'name': 'version', 'value': version}
            ]
        }
    trigger_jenkins_webhook(jenkins_url_east,headers,payload)
    time.sleep(testing_time)
    trigger_jenkins_webhook(jenkins_url_west,headers,payload)
