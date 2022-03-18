#!/usr/local/bin/python3 
 
from __future__ import print_function

import sys
import os
import hashlib
import yaml
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '163TTTMqbu_og6vOaRie8X-LGADXw-xZ904SU9ypDr38'
SAMPLE_RANGE_NAME = 'Haiku!A2:C'


def main():
    log('Connecting to sheets API...')

    api_key = os.environ.get('GCP_API_KEY')
    if not api_key:
        log('ERROR: no GCP_API_KEY environment variable specified')
        return 2

    if len(sys.argv) != 2:
        log('ERROR: usage: ' + sys.argv[0] + ' <output directory>')
        return 1
    outdir = sys.argv[1]
    if not outdir:
        log('ERROR: usage: ' + sys.argv[0] + ' <output directory>')
        return 1
    if not os.path.exists(outdir):
        log('Creating output directory: ' + outdir)
        os.makedirs(outdir)
    
    try:
        service = build('sheets', 'v4', developerKey=api_key)

        # Call the Sheets API
        sheet = service.spreadsheets()

        log('Fetching raw data...')
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            log('No data found.')
            return

        log('Transforming results to yaml files in ' + outdir)
        ctr = 0
        for row in values:
            if len(row) >= 3:
                row_id = hashlib.sha1(row[0].encode()).hexdigest()
                text = list(filter(None, row[2].split('\n')))
                haiku = [{
                    '_id': row_id,
                    'timestamp': datetime.datetime.strptime(row[0], '%m/%d/%Y %H:%M:%S').isoformat(),
                    'author': row[1],
                    'text': text
                }]
                with open(outdir + '/' + row_id + r'.yaml', 'w') as file:
                    yaml.dump(haiku, file)
                    log('Wrote ' + row_id + '.yaml')
                ctr += 1
        
        log('Generated ' + str(ctr) + ' files')
    except HttpError as err:
        log(err)

def log(msg):
    print(msg, file=sys.stderr)

if __name__ == '__main__':
    main()