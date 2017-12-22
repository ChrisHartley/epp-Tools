import xlsxwriter
import psycopg2
import datetime
import argparse

person_query = """
select u.first_name AS "First Name",
u.last_name AS "Last Name",
'' AS "Party Number",
profile.external_system_id as "External System Id",
'' AS "Organization External System Id",
'' AS "Organization Party Number",
'' AS "Update",
profile.mailing_address_line1 AS "Address.Address 1",
profile.mailing_address_city AS "Address.City",
CASE
    WHEN profile.mailing_address_state ilike 'Indiana' THEN 'IN'
    ELSE profile.mailing_address_state
END
 AS "Address.State",
profile.mailing_address_zip AS "Address.Postal Code",
profile.mailing_address_line2 AS "Address.Address 2",
'' AS "Address.Country",
'' AS "Address.County",
'' AS "Address.Latitude",
'' AS "Address.Longitude",
u.email as "Email",
'Owner|Buyer' AS "Function",
'' AS "Middle",
'' AS "Prefix",
'' AS "Suffix",
profile.phone_number AS "Telephone",
'' AS "TIN",
'' AS "Title"
FROM property_inventory_property p
LEFT JOIN applications_application app ON app.id = p.buyer_application_id
LEFT JOIN auth_user u ON u.id = app.user_id
LEFT JOIN applicants_applicantprofile profile ON profile.user_id = u.id
--LEFT JOIN applicants_organization org ON org.id = u.id
WHERE
app.organization_id IS NULL and p.buyer_application_id is not null
GROUP BY u.first_name, u.last_name, profile.external_system_id, profile.mailing_address_line1, profile.mailing_address_city, profile.mailing_address_state, profile.mailing_address_zip, profile.mailing_address_line2, u.email, profile.phone_number
"""

organization_query = """
SELECT
'External' as "Class",
org.name AS "Legal Name",
u.first_name AS "Contact.First Name",
u.last_name AS "Contact.Last Name",
'' AS "Party Number",
org.external_system_id AS "External System Id",
'' as "Contact.External_System_Id", --profile.external_system_id AS "Contact.External System Id",
'' AS "Update",
org.mailing_address_line1 AS "Address.Address 1",
org.mailing_address_city AS "Address.City",
org.mailing_address_state AS "Address.State",
org.mailing_address_zip AS "Address.Postal Code",
org.mailing_address_line2 AS "Address.Address 2",
'' AS "Address.Country",
'' AS "Address.County",
'' AS "Address.Latitude",
'' AS "Address.Longitude",
'' AS "Business Type",
'' AS "DBA Name",
'' AS "DUNS",
'' AS "EIN",
org.email AS "Email",
'Owner|Buyer' AS "Function",
'' AS "Industry",
org.phone_number AS "Telephone"

FROM property_inventory_property p
LEFT JOIN applications_application app ON app.id = p.buyer_application_id
LEFT JOIN auth_user u ON u.id = app.user_id
LEFT JOIN applicants_applicantprofile profile ON profile.user_id = app.user_id
LEFT JOIN applicants_organization org ON org.id = app.organization_id
WHERE
org.name is not null
GROUP BY org.name, u.first_name, u.last_name, org.external_system_id, profile.external_system_id, org.mailing_address_line1, org.mailing_address_city, org.mailing_address_state, org.mailing_address_zip, org.mailing_address_line2, org.email, org.phone_number order by org.name

"""


organization_header = ['Class','Legal Name','Contact.First Name','Contact.Last Name','Party Number','External System Id','Contact.External System Id','Update','Address.Address 1','Address.City','Address.State','Address.Postal Code','Address.Address 2','Address.Country','Address.County','Address.Latitude','Address.Longitude','Business Type','DBA Name','DUNS','EIN','Email','Function','Industry','Telephone'
]

person_header = ['First Name','Last Name','Party Number','External System Id','Organization External System Id','Organization Party Number','Update','Address.Address 1','Address.City','Address.State','Address.Postal Code','Address.Address 2','Address.Country','Address.County','Address.Latitude','Address.Longitude','Email','Function','Middle','Prefix','Suffix','Telephone','TIN','Title'
]

conn_string = "host='localhost' dbname='blight_fight' user='chris' password='chris'"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()


workbook = xlsxwriter.Workbook('party-import-{0}.xlsx'.format(datetime.date.today(),))
organization_worksheet = workbook.add_worksheet('Organization')
person_worksheet = workbook.add_worksheet('Person')

for i in range(len(organization_header)):
    organization_worksheet.write(0, i, organization_header[i])

cursor.execute(organization_query)

for index,prop in enumerate(cursor.fetchall(), 1):
    for i in range(len(prop)):
        organization_worksheet.write(index, i, prop[i])


for i in range(len(person_header)):
    person_worksheet.write(0, i, person_header[i])

cursor.execute(person_query)

for index,prop in enumerate(cursor.fetchall(), 1):
    for i in range(len(prop)):
        person_worksheet.write(index, i, prop[i])


workbook.close()
