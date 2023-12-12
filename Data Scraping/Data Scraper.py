from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import re
import time

# IMPORTANT: Data Scraper.py only works for batting statistics for now
# ASSUMPTION: Webpage is sorted in descending order of date (latest is first) in the target webpage
# ACTION: Ensure above is observed before pasting URL in "URL for data.txt" file and running "Data Scraper.py"

# Read URL from txt file
with open("URL for data.txt") as f: 
    url = f.read()

data = []
i=1
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach",True)
driver = webdriver.Chrome(options=chrome_options) 
driver.get(url)
time.sleep(2)   #Sleep time to be adjusted based on internet connection

# Get the column names from the web page
table_header = driver.find_element(By.XPATH, "//table[@class='engineTable']/thead/tr")
column_names = [col.text for col in table_header.find_elements(By.TAG_NAME, "th")]

# Load the existing data from the CSV file if already present
try:
    df_existing = pd.read_csv('cricket_data.csv')
    df_existing['Start Date'] = pd.to_datetime(df_existing['Start Date'])
    # 'Start Date' of the latest entry is taken. 
    latest_date = pd.to_datetime(df_existing['Start Date']).max()
    latest_date = latest_date.strftime('%d-%b-%Y')
    print(f"Latest entry date in CSV file is {latest_date}")
except FileNotFoundError:
    # If the file does not exist, create an empty DataFrame and set the latest_date to an old date
    df_existing = pd.DataFrame(columns=column_names)
    latest_date = pd.to_datetime('1900-01-01').date()
    latest_date = latest_date.strftime('%d-%b-%Y')

# Loop to navigate to all pages that contain data relevant to user, using 'Next'
# And run till the latest entry, if present, in CSV file if matched with scraped data
break_while = False
while break_while == False:
    page_data = driver.find_elements(By.CLASS_NAME,'data1') # Get all the rows from the page
    for row_data in page_data:
        row = row_data.find_elements(By.TAG_NAME,'td')
        row_list = [k.text for k in row]
        data_dict = dict(zip(column_names, row_list)) 
        data_dict['Start Date'] = pd.to_datetime(data_dict['Start Date'], dayfirst=False)
        data_dict['Start Date'] = data_dict['Start Date'].strftime('%d-%b-%Y')
        # Checks 'Start Date' in existing file to update data_dict accordingly.
        if data_dict['Start Date'] == latest_date:  
            break_while  = True
            break
        data.append(row_list)
        print(f"row {i} added")
        i += 1
    if break_while == False:    # Page navigation
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
        time.sleep(2)   #Sleep time to be adjusted based on internet connection

df = pd.DataFrame(data, columns=column_names)

# Below section checks whether scraped data from the run needs to be concatenated with existing data
# Dataframe is modified to be readable and useful for further analysis
if not df.empty:
    # Removing unwanted columns/data
    df = df.drop(['Mins',''], axis=1) 
    df['Runs'] = df['Runs'].str.replace("*", "")
    df['Opposition'] = df['Opposition'].str.replace("v ", "")
    
    df.insert(1, 'Country', '') # Extracts player's country name and inserts it as a new column in the dataframe
    df['Country'] = df['Player'].str.extract('\\((.*?)\\)', expand=False)

    df['Player'] = df['Player'].apply(lambda x: re.sub(r' \(.*?\)', '', x)) # Removes country name from 'Player'
    if not df_existing.empty:   # Concat function only if BOTH df and df_existing have data
        df = df.astype(df_existing.dtypes.to_dict())    # Match datatypes of both df and df_existing for concat
        df = pd.concat([df, df_existing], ignore_index=True)
    
    df = df.drop_duplicates()
    df.to_csv('cricket_data.csv', index=False)
    print(df.head())
    print("Your data set has been updated")
else:
    print("Your data set is up to date")
driver.close()