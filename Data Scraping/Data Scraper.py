from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
import csv

#Module to clean data and change data types for manipulation/analysis
def data_clean(Data):
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

#Module to write the data one entry (one row) at a time
def write_to_csv(Data):
    with open('Cricinfo.csv', 'a', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(Data)
        f.close()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach",True)

# Reads url from txt file
with open("URL for data.txt") as f: 
    url = f.read()

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
i=1 # Counter

#Gets column names for cricket stats
heading = driver.find_element(By.TAG_NAME,"thead")
attributes = heading.find_elements(By.TAG_NAME,'th')
attr = [i.text for i in attributes]
#Cleaning of column names
attr.insert(1,"Country")
attr.remove('Mins')
attr.remove('')
attr.remove('') 
write_to_csv(attr) # csv file created and column names added
print("csv file created")

while True:
    page_data = driver.find_elements(By.CLASS_NAME,'data1') #Get all the rows from the page
    for row_data in page_data:
        row = row_data.find_elements(By.TAG_NAME,'td')
        row_list = [k.text for k in row]
        row_list = data_clean(row_list)
        write_to_csv(row_list)
        print(f"row {i} added to csv file")
        i += 1
    try:
        nextpage = driver.find_element(By.LINK_TEXT, "Next")
        url_nextpage = nextpage.get_attribute('href')
        print("next page")
    except NoSuchElementException:
        print("end")
        driver.close()
        break  
    driver.close()
    driver = webdriver.Chrome(options=chrome_options) 
    driver.get(url_nextpage)