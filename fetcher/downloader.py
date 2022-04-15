import datetime
from pprint import pprint

from googleapiclient.discovery import build
from yaml_file_types import Haiku

SPREADSHEET_ID = '163TTTMqbu_og6vOaRie8X-LGADXw-xZ904SU9ypDr38'
RANGE_NAME = 'Haiku!A2:D'

def fetch_haiku(api_key):
  """Obtains Haiku objects from the haiku spreadsheet"""
  rows = download_rows(api_key)
  return process_rows(rows)

def download_rows(api_key):
  """Downloads raw data from the Haiku spreadsheet"""
  service = build('sheets', 'v4', developerKey=api_key)
  sheet = service.spreadsheets()
  result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                              range=RANGE_NAME).execute()
  rows = result.get('values', [])
  return rows

def process_rows(rows):
  """Processes an array of table rows"""
  ctr_fail = 0
  result = []
  for row in rows:
    haiku = process_row(row)
    if haiku:
      result.append(haiku)
    else:
      ctr_fail += 1
  print('Done processing rows. ' + str(len(result)) + ' rows ok, ' + str(ctr_fail) + ' rows ignored.')
  return result

def process_row(row):
  """Given a raw table row, return a Haiku object, or False if the row is invalid"""
  pprint(row)
  if len(row) < 4:
    return False

  date = datetime.datetime.strptime(row[0], '%m/%d/%Y %H:%M:%S')
  author = row[1]
  text = list(filter(None, row[2].split('\n')))
  topics = [topic.strip() for topic in row[3].split(';')] if row[3] else []
  
  return Haiku(date, author, text, topics)
