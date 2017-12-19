API_ENDPOINT = 'https://api.epropertyplus.com/landmgmt/api/'

#POST /landmgmtpub/remote/public/property/getPublishedProperties


json_query = {
    "criterias": [
        {
            "name": "featured",
            "value": "Yes",
            "operator": "EQUALS"
        },
    ]
}

import json
from requests import Request, Session
#URL = 'https://public-indy.epropertyplus.com/landmgmtpub/remote/public/property/getPublishedProperties'
URL = 'https://indysbx.epropertyplus.com/landmgmt/api/property/summary'
params = {
    'page':1,
    'limit':10,
    'json': {"criterias": [{"name": "featured","value": "Yes","operator": "EQUALS"}]},
}

()
s = Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (ePPHelper Class)',
    'Content-Type': 'application/json',
    #'x-strllc-authkey':  'Y2hyaXMuaGFydGxleUByZW5ld2luZGlhbmFwb2xpcy5vcmc6NDA6MTU0NDkxOTQ0ODk3NjplMmZiODc1MWQ5YzYxM2NiN2ExMDdmYjQ3NTU1ZjIwMzNlYTZhODJlZjNjMmRkZGNkMDQ5MzJjNmEzYTBjODgw',
    'x-strllc-authkey': 'Y2hyaXMuaGFydGxleUByZW5ld2luZGlhbmFwb2xpcy5vcmc6NDQ6MTU0Mzk1NzY0NzYyMDo4OWUxYzNlY2E0NmZjZDNjMzcwY2E5MzhhNWJiNjdmNWUwM2MzNjhlOGU5MDcyOWYzNjc3OGMxYWVkYWY2YzVk',
    'Accept': 'application/json',
}
s.headers.update(headers)
r = s.post(URL, data=json.dumps(params))
print( 'Request Headers',r.request.headers)
print( 'Request Body', r.request.body)
print( 'Request URL',r.url)
print( 'Request Headers',r.headers)
print( r.json)
print( r.text)
