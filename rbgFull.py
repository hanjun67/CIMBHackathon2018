# This script is to generate random number of entries
import random
import xlsxwriter
import functools
import uuid
import names
import datetime as dt

# Predefined variable
length = 2
data_id = []
national_id = []
date_of_birth = []
full_name = []
postal_code = []
gender = []
nationality = []

startdate = dt.date(1950,1,1)
nbdays = (dt.date.today()-startdate).days

# Using random to instill randomize the number
for i in range(length):
    # key
    data_id.append(i+1)
    # National ID Generator
    national_id.append(str(uuid.uuid4()))
    # Name generator
    full_name.append(names.get_full_name())
    # Date of birth generator
    d = random.randint(0,nbdays)
    date_of_birth.append(startdate + dt.timedelta(days=d))
    # Postal code generator
    # assume postal code is 6 digit number
    postal_code.append(random.randint(100000,999999))
    # Nationality generator
    nationality.append('Singaporean')
    # Gender generator
    gender.append(random.randint(0,1))
    if gender[i] == 0:
        gender[i] = "M"
    elif gender[i] == 1:
        gender[i] = "F"

## This is just for excel view of the particulars
# Write the Random Generated Data into the xlsx
xlFile = 'RGB.xlsx'
workbook = xlsxwriter.Workbook(xlFile)
worksheet = workbook.add_worksheet()
row = 0

for i in range(length):
	worksheet.write(row, 0, i+1)
	worksheet.write(row, 1, national_id[i])
	worksheet.write(row, 2, full_name[i])
	worksheet.write(row, 3, date_of_birth[i])
	worksheet.write(row, 4, postal_code[i])
	worksheet.write(row, 5, nationality[i])
	worksheet.write(row, 6, gender[i])
	row += 1
workbook.close()

## Table creation and pump all the data into SQLite
# This script is to force the Excel data into table.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tableDefine import *

# Query to the database
engine = create_engine('sqlite:///data.db', echo = True)

# Create a Session
Session = sessionmaker(bind=engine)
session = Session()

# Pump the data into the class
for i in range(len(data_id)):
    particulars_data = Particulars(data_id[i], national_id[i], full_name[i], date_of_birth[i], postal_code[i], nationality[i], gender[i], None)
    session.add(particulars_data)
    credentials_data = Credentials('user' + str(data_id[i]), '1234', data_id[i])
    session.add(credentials_data)
    
# commit the record the database
session.commit()

# Update 1 user with account balance
session.query(Credentials).filter(Credentials.user_name ==  'user1').update({'acc_balance':10000})
session.commit()
