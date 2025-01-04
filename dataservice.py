from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

class DataService: 

    def __init__(self): 
        self.driver = webdriver.Chrome()
        #self.driver.get("https://my.raceresult.com/309137/")
        self.handle_cookies()
        self.show_all_buttons = self.driver.find_elements(By.CLASS_NAME, "aShowAll")
        self.show_all_buttons[1].click()
        time.sleep(3)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Main
                                            
    def set_source(self, url):

# Setup ChromeDriver
driver = webdriver.Chrome()
driver.get("https://my.raceresult.com/309137/")

# Warten und Cookie-Banner akzeptieren (falls vorhanden)
try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "cookieChoiceDismiss"))  # Button identifizieren
    ).click()
    print("Cookie-Banner geschlossen.")
except:
    print("Kein Cookie-Banner gefunden.")

time.sleep(1)

show_all_buttons = driver.find_elements(By.CLASS_NAME, "aShowAll")

show_all_buttons[1].click()

time.sleep(3)

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "MainTable"))
)

page = driver.page_source
soup = BeautifulSoup(page, "html.parser")

table = soup.find("table", {"class": "MainTable"})

columns = []

header_cols = table.find("thead").find_all("th")



for i in range(len(header_cols)): 
    columns.append(header_cols[i].text)

print(columns)
columns = columns[1:-1]
print(columns)

df = pd.DataFrame(columns=columns)

rows = table.find_all("tr")

for row in rows: 
    values = []
    cols = row.find_all("td")
    if cols:  
        for col in range(len(cols)): 
            values.append(cols[col].text)
        values = values[1:-1]
        print(values)
        df.loc[len(df)]=values