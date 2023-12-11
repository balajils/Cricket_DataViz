from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from datetime import datetime
import re

data = [] 

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach",True)

# Reads url from txt file
with open("URL for data.txt") as f: 
    url = f.read()

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

table_header = driver.find_element(By.XPATH, "//table[@class='engineTable']/thead/tr")
column_names = [ele.text for ele in table_header.find_elements(By.TAG_NAME, "th")]

# Load the existing data from the CSV file
try:
    df_existing = pd.read_csv('cricinfo_data.csv')
    df_existing['Start Date'] = pd.to_datetime(df_existing['Start Date'], format='%d-%m-%Y')
    latest_date = pd.to_datetime(df_existing['Start Date']).max()
    latest_date = latest_date.strftime('%d-%m-%Y')
except FileNotFoundError:
    # If the file does not exist, create an empty DataFrame and set the latest date to an old date
    df_existing = pd.DataFrame(columns=column_names)
    latest_date = pd.to_datetime('1900-01-01').date()
    latest_date = latest_date.strftime('%d-%m-%Y')
i=1   
break_while = False
while break_while == False:
    page_data = driver.find_elements(By.CLASS_NAME,'data1') # Get all the rows from the page
    for row_data in page_data:
        row = row_data.find_elements(By.TAG_NAME,'td')
        row_list = [k.text for k in row]
        data_dict = dict(zip(column_names, row_list))
        data_dict['Start Date'] = pd.to_datetime(data_dict['Start Date'], dayfirst=False)
        data_dict['Start Date'] = data_dict['Start Date'].strftime('%d-%m-%Y')
        if data_dict['Start Date'] == latest_date:
            break_while  = True
            break
        data.append(row_list)
        print(f"row {i} added")
        i += 1
    if break_while == False:
        try:
            nextpage = driver.find_element(By.LINK_TEXT, "Next")
            url_nextpage = nextpage.get_attribute('href')
            print("next page")
        except NoSuchElementException:
            print("last page")
            break
        driver.close()
        driver = webdriver.Chrome(options=chrome_options) 
        driver.get(url_nextpage)

df = pd.DataFrame(data, columns=column_names)
df = pd.concat([df_existing, df])
df = df.drop_duplicates()
df = df.drop(['Mins',''], axis=1)

df['Runs'] = df['Runs'].str.replace("*", "")
df['Opposition'] = df['Opposition'].str.replace("v ", "")
df.insert(1, 'Country', '')
df['Country'] = df['Player'].str.extract('\\((.*?)\\)', expand=False)
df['Player'] = df['Player'].apply(lambda x: re.sub(r' \(.*?\)', '', x))

df.to_csv('cricket_data.csv', index=False)
print(df.head())
driver.close()