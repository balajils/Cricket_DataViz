import pandas as pd
import numpy as np
import matplotlib as plt
import os


os.chdir("../Cricket_DataViz/Data Scraping")
path = "Cricinfo.csv"

data = pd.read_csv(path)
print(data.head())

a = data.query('Country == "IND"')
print(a.head())