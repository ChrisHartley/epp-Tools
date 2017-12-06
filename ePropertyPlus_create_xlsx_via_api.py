### This is a utility to create an Excel spreadsheet of properties from the
### ePropertyPlus API. One use case could be to have an always up-to-date
### inventory spreadsheet available for users to download.
### GPL v3 license, by Chris Hartley, Renew Indianapolis.
### chris.hartley@renewindianapolis.org
from urllib2 import urlopen
from urllib import quote
import json
import xlsxwriter
from os.path import getmtime
import datetime

# Store your secret API key in a separate file 'api_key.py' and import the
# variable here. Or you can just put the key here, if you aren't going to
# re-commit to source control
try:
    from api_key import API_KEY
except ImportError:
    API_KEY = ''

API_ENDPOINT = 'https://indysbx.epropertyplus.com/landmgmt/api/property/summary/'

# Edit the query as necessary
json_query = '{"criterias":[{"name":"active","value":"Yes","operator":"EQUALS"},{"name":"published","value":"Yes","operator":"EQUALS"}]}'
FILENAME = '/tmp/Inventory-Export.xlsx'
REFRESH_SECONDS = 300
# Define the fields to write to the spreadsheet.
# Column name, field name from response json.
fields = (
    ('Parcel', 'parcelNumber'),
    ('Street Address', 'propertyAddress1'),
    ('ZIP Code','postalCode'),
    ('Price', 'askingPrice'),
)

try:
    mtime = getmtime(FILENAME)
except OSError:
    mtime = 0
tdelta = datetime.datetime.now() - datetime.datetime.fromtimestamp(mtime)

if tdelta.total_seconds() > REFRESH_SECONDS: # 5 minutes
    print 'File stale, re-fetching'
    workbook = xlsxwriter.Workbook(FILENAME)
    worksheet = workbook.add_worksheet('Available Inventory')

    url = '{0}?x-strllc-authkey={1}&json={2}&page=1&limit=50000'.format(API_ENDPOINT,API_KEY,quote(json_query))
    response = urlopen(url)
    json_obj = json.load(response)

    # Write column names across the first row.
    for indx,field in enumerate(fields):
        worksheet.write(0, indx, field[0])

    # For each record returned, write the fields we care about to the spreadsheet.
    for row,record in enumerate(json_obj['rows'], start=1):
        for indx,field in enumerate(fields):
            worksheet.write(row, indx, record[field[1]])
    workbook.close()
else:
    print 'File cached, not re-fetching.'
