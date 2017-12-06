### This is a utility to create an Excel spreadsheet of properties from the
### ePropertyPlus API. One use case could be to have an always up-to-date
### inventory spreadsheet available for users to download.
### GPL v3 license, by Chris Hartley, Renew Indianapolis.
### chris.hartley@renewindianapolis.org
from requests import Request, Session
import xlsxwriter
from os.path import getmtime
import datetime
from ePropertyPlus_api import ePPHelper

# Store your secret API key in a separate file 'api_key.py' and import the
# variable here. Or you can just put the key here, if you aren't going to
# re-commit to source control
try:
    from api_key import API_KEY
except ImportError:
    API_KEY = ''

API_ENDPOINT = 'https://indysbx.epropertyplus.com/landmgmt/api/'

# Edit the query as necessary
api_resource = 'property/summary'
json_query = '{"criterias":[{"name":"active","value":"Yes","operator":"EQUALS"},{"name":"published","value":"Yes","operator":"EQUALS"}]}'

FILENAME = '/tmp/Inventory-Export.xlsx'
REFRESH_SECONDS = 3
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

    epp = ePPHelper(API_KEY, API_ENDPOINT)
    json_obj = epp.query(api_resource, json_query)

    if json_obj['success'] == True:

        # Write column names across the first row.
        for indx,field in enumerate(fields):
            worksheet.write(0, indx, field[0])

        # For each record returned, write the fields we care about to the spreadsheet.
        for row,record in enumerate(json_obj['rows'], start=1):
            for indx,field in enumerate(fields):
                worksheet.write(row, indx, record[field[1]])
    else:
        print "Endpoint returned success = false"
        print json_obj
    workbook.close()
else:
    print 'File cached, not re-fetching.'
