import xlsxwriter
import psycopg2
import datetime
import argparse

master_query = """
SELECT distinct
parcel_c as "Parcel Number",
r.property_status as "Property Status",
r.property_class as "Property Class",
'' as "Owner Party Number",
'INDY1000' as "Owner Party External System Id",
p."streetAddress" as "Property Address.Address1",
'' as "Property Address.Address2",
'INDIANAPOLIS' as "Property Address.City",
'MARION' as "Property Address.County",
'IN' as "Property Address.State",
p.zipcode as "Property Address.Postal Code",
'' as "Status Date",
'' as "Property Manager Party Number",
'INDY1003' as "Property Manager Party External System Id",
'' as "Update",
'' as "Available",
'' as "Foreclosure Year",
r.inventory_type as "Inventory Type",
c."Legal_Description" as "Legal Description",
'' as "Listing Comments",
'INDY1007' as "Maintenance Manager Party External System Id",
'' as "Maintenance Manager Party Number",
p.estsqft as "Square Footage",
CASE WHEN ST_XMax(st_transform(p.geom, 2965)) - ST_XMin(st_transform(p.geom, 2965)) < ST_YMax(st_transform(p.geom, 2965)) - ST_YMin(st_transform(p.geom, 2965)) THEN round(ST_XMax(st_transform(p.geom, 2965)) - ST_XMin(st_transform(p.geom, 2965)))::text ELSE round(ST_YMax(st_transform(p.geom, 2965)) - ST_YMin(st_transform(p.geom, 2965)))::text
END as "Parcel Width",
CASE WHEN ST_XMax(st_transform(p.geom, 2965)) - ST_XMin(st_transform(p.geom, 2965)) > ST_YMax(st_transform(p.geom, 2965)) - ST_YMin(st_transform(p.geom, 2965)) THEN round(ST_XMax(st_transform(p.geom, 2965)) - ST_XMin(st_transform(p.geom, 2965)))::text ELSE round(ST_YMax(st_transform(p.geom, 2965)) - ST_YMin(st_transform(p.geom, 2965)))::text
END as "Parcel Length",
'N' as "Published",
r.tag as "Tags",
st_y(st_transform(st_centroid(p.geom), 4326)) as "Latitude",
st_x(st_transform(st_centroid(p.geom), 4326)) as "Longitude",
st_astext(st_transform(p.geom, 4326)) as "Parcel Boundary",
ci.geoid as "Census Tract",
NULL as "Congressional District",
NULL as "Legislative District",
cd.description as "Local District",
n.name as "Neighborhood",
s.corporation as "School District",
NULL as "Voting Precinct",
z.code1 as "Zoned As",
NULL as "Acquisition Amount",
CASE
   WHEN r.property_status != 'Sold' and to_char(c."Deed_Date", 'YYYY') = '2017' THEN to_char(c."Deed_Date", 'MM/DD/YYYY') ELSE
   NULL
END as "Acquisition Date",
'' as "Acquisition Method",
'' as "Sold Amount",
CASE
    WHEN r.property_status = 'Sold' THEN to_char(c."Deed_Date", 'MM/DD/YYYY') ELSE
    NULL
END as "Sold Date",
NULL as "Actual Disposition",
'' as "Asking Price",
CASE
    WHEN c."Gross_Value" is not null THEN '2017'
END as "Assessment Year",
c."Gross_Value" as "Current Assessment",
NULL as "Minimum Bid Amount",
NULL as "Block Condition",
'' as "Brush Removal",
'' as "Cleanup Assessment",
'' as "Demolition Needed",
'' as "Environmental Cleanup Needed",
m.mva_cat as "Market Condition",
'' as "Potential Use",
'' as "Property Condition",
'' as "Property of Interest",
'N' as "Quiet Title",
'' as "Rehab Candidate",
'' as "Target Disposition",
'' as "Trash Removal",
'' as "Custom.BEP Mortgage Expiration Date",
'' as "Custom.BLC Number",
initcap(cdc.name) as "Custom.CDC",
'' as "Custom.Grant Program",
'' as "Custom.Sales Program"

FROM dmd_property_load r
LEFT JOIN parcels p on p.parcel_c = r.parcel
LEFT JOIN counter_book_2018 c on c."Parcel_Number" = p.parcel_c
LEFT JOIN census_tract_marion_county_income ci on st_within(p.geom, ci.geometry)
LEFT JOIN neighborhoods n on st_within(p.geom, n.geom)
LEFT JOIN mva_areas m ON st_within(p.geom, m.geom)
LEFT JOIN school_districts s ON st_within(p.geom, s.geom)
LEFT JOIN zoning z ON st_within(st_centroid(p.geom), z.geom)
LEFT JOIN council_districts cd ON st_within(st_centroid(p.geom), cd.geom)
LEFT JOIN property_inventory_cdc cdc on st_within(st_centroid(p.geom), st_transform(cdc.geometry, 2965))
"""

parser = argparse.ArgumentParser(description='Create ePropertyPlus property xlsx from input csv')
parser.add_argument('-f', '--file', required=True, help='input csv file')
args = parser.parse_args()

header = ['Parcel Number', 'Property Status', 'Property Class', 'Owner Party Number', 'Owner Party External System Id', 'Property Address.Address1', 'Property Address.Address2', 'Property Address.City', 'Property Address.County', 'Property Address.State', 'Property Address.Postal Code', 'Status Date', 'Property Manager Party Number', 'Property Manager Party External System Id', 'Update', 'Available', 'Foreclosure Year', 'Inventory Type', 'Legal Description', 'Listing Comments', 'Maintenance Manager Party External System Id', 'Maintenance Manager Party Number', 'Parcel Square Footage', 'Parcel Length', 'Parcel Width', 'Published', 'Tags', 'Latitude', 'Longitude', 'Parcel Boundary', 'Census Tract', 'Congressional District', 'Legislative District', 'Local District', 'Neighborhood', 'School District', 'Voting Precinct', 'Zoned As', 'Acquisition Amount', 'Acquisition Date', 'Acquisition Method', 'Sold Amount', 'Sold Date', 'Actual Disposition', 'Asking Price', 'Assessment Year', 'Current Assessment', 'Minimum Bid Amount', 'Block Condition', 'Brush Removal', 'Cleanup Assessment', 'Demolition Needed', 'Environmental Cleanup Needed', 'Market Condition', 'Potential Use', 'Property Condition', 'Property of Interest', 'Quiet Title', 'Rehab Candidate', 'Target Disposition', 'Trash Removal ', 'Custom.BEP Mortgage Expiration Date', 'Custom.BLC Number', 'Custom.CDC', 'Custom.Grant Program', 'Custom.Sales Program'
]

header_text_fields = []

conn_string_gis = "host='localhost' dbname='epp' user='chris' password='chris'"
conn_gis = psycopg2.connect(conn_string_gis)
cursor = conn_gis.cursor()

cursor.execute('truncate table dmd_property_load')
cursor.execute("copy dmd_property_load from %s csv header",(args.file,))
cursor.execute(master_query)

workbook = xlsxwriter.Workbook('property-import-{0}.xlsx'.format(datetime.date.today(),))
worksheet = workbook.add_worksheet('PropertyDescription')
text_format = workbook.add_format({'num_format': '@'})

for i in range(len(header)):
    worksheet.write(0, i, header[i])

for index,prop in enumerate(cursor.fetchall(), 1):
    print(prop)
    for i in range(len(prop)):
        #print(prop[i])
        #print(header[i])
        #print(header_text_fields.index(header[i]))
        try:
            if header_text_fields.index(header[i]):
                print("Text Field! {0}".format(header[i]))
                worksheet.write(index, i, prop[i], text_format) # write parcel numbers as text
        except ValueError:
            worksheet.write(index, i, prop[i])

workbook.close()
