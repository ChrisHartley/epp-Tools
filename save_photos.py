from ePP_simple_api import ePPHelper
import requests
from tqdm import tqdm

import argparse

parser = argparse.ArgumentParser(description='Generate SQL to add property to Blight Fight')
parser.add_argument('-p', '--parcel', type=int, help='parcel number', required=False)
args = parser.parse_args()

epp = ePPHelper(sandbox=False, debug=False)

json_query = '{"criterias":[{"name":"parcelNumber","value":"%s","operator":"EQUALS"}]}' % args.parcel

props = epp.get_property_search(json_query=json_query)

for row in props['rows']:
    print('Downloading images for parcel {0}, id {1}'.format(args.parcel,row['id'],))
    image_results = epp.get_image_list(row['id'])
    for image_result in tqdm(image_results['rows']):
        img_id = image_result['id']
        with open(image_result['filename'], 'wb') as f:
            f.write(epp.get_image(img_id))
