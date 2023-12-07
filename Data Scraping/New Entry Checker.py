# The programme comes to use after running 'Data Scraper.py' and creating 'Cricinfo.csv'
# Once data for a query is collected, this programme can be run if there has been new
# entries to the orginal query since the date of data collection
# IMPORTANT: The programme is written to only consider new entry addtion < 200 (one page)

from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
import csv
import os

#Module to clean data and change data types for manipulation/analysis
def data_clean(Data):
    #Below commands are to clean the data and change data types for further analysis
    Data.insert(1,Data[0][Data[0].index('(')+1:-1])
    Data[0]=Data[0][:Data[0].index('(')-1]
    Data.remove('')
    Data.remove('')
    del Data[3]
    Data[8]=Data[8][2:]
    if Data[2][len(Data[2])-1]=='*':
        Data[2]=Data[2][:-1]
    Data[2:6] = [int(i) if i.isdigit() else 0 for i in Data[2:6]]
    Data[6]=float(Data[6])
    Data[7]=int(Data[7])
    Data[10]=datetime.strptime(Data[10],'%d %b %Y').date()
    return Data

# Reads url from txt file
with open("URL for data.txt") as f: 
    url = f.read()

# Load your CSV file
with open("Cricinfo.csv") as f: 
    reader  = csv.reader(f)
    heading = next(reader)
    first_row = next(reader)
df = pd.read_csv('Cricinfo.csv')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach",True)

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

page_data = driver.find_elements(By.CLASS_NAME,'data1') #Get all the rows from the page
for row_data in page_data:
    row = row_data.find_elements(By.TAG_NAME,'td')
    row_list = [k.text for k in row]
    row_list = data_clean(row_list)
    data_dict = dict(zip(heading, row_list))
    data_dict['Start Date'] = pd.to_datetime(data_dict['Start Date'], dayfirst=True)
    data_dict['Start Date'] = data_dict['Start Date'].strftime('%d-%m-%Y')
    if data_dict['Start Date'] == first_row[-1]:
        print("table up to date")
        break
    else:
        df = pd.concat([pd.DataFrame(data_dict, index=[0]), df], ignore_index=True)
        print("new row added")

driver.close()
df['Start Date'] = pd.to_datetime(df['Start Date'], dayfirst=True)
df = df.sort_values(by='Start Date', ascending=False)
df['Start Date'] = df['Start Date'].dt.strftime('%d-%m-%Y')

# Updated DataFrame Saved back to CSV
df.to_csv('Cricinfo.csv', index=False)