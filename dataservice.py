from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import logging
import time
import re 

# Constants for timeouts and indices
COOKIE_BANNER_TIMEOUT = 5
SHOW_ALL_BUTTON_INDEX = 1
MAIN_TABLE_TIMEOUT = 10

class DataService:
    """
    A class to interact with a webpage, handle cookies, and extract table data as a DataFrame.
    """
    def __init__(self):
        """
        Initializes the DataService with a Selenium WebDriver.
        """
        self.driver = None
        self.source = None
        self.date = None 
        self.location = None 
        self.title = None 
        self.soup = None 
        self.dataFrame = None
        print("[DEBUG] DataService initialized.")

    def set_source(self, url):
        """
        Navigates to the specified URL using the WebDriver.
        """
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        self.source = url
        print(f"[DEBUG] Navigated to URL: {url}")
        print(f"[DEBUG] Source set to: {self.source}")

    def handle_cookie_banner(self):
        """
        Attempts to close the cookie banner if it is present on the webpage.
        """
        print(f"[DEBUG] Current source: {self.source}")
        time.sleep(2)

        try:
            WebDriverWait(self.driver, COOKIE_BANNER_TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "cookieChoiceDismiss"))  # Button identifier
            ).click()
            print("Cookie-Banner geschlossen.")
        except Exception as e:
            print(f"Kein Cookie-Banner gefunden: {e}")

        time.sleep(1)

    def click_show_all_buttons(self):
        """
        Clicks the "Show All" button on the webpage.
        """
        try:
            show_all_buttons = self.driver.find_elements(By.CLASS_NAME, "aShowAll")
            if show_all_buttons and len(show_all_buttons) > SHOW_ALL_BUTTON_INDEX:
                show_all_buttons[SHOW_ALL_BUTTON_INDEX].click()
                time.sleep(3)
                logging.info("'Show All' button clicked.")
            else:
                logging.warning("No 'Show All' button found at the expected index.")
        except Exception as e:
            logging.error(f"Error clicking 'Show All' button: {e}")
    
    def create_soup(self):
        """
        Creates a BeautifulSoup object from the current page source.

        Returns:
            BeautifulSoup: A BeautifulSoup object of the current page source.
        """
        page = self.driver.page_source
        self.soup = BeautifulSoup(page, "html.parser")
        return BeautifulSoup(page, "html.parser")

    def get_metadata(self):
        """
        Extracts the title of the webpage and other metadata.

        Returns:
            str: The title and metadata of the webpage.
        """

        # Try to locate the "HomepageHeadTitle" div element
        header = self.soup.find("div", {"class": "HomepageHeadTitle"}).text

        cleaned_header = header.strip().replace('\t', '').replace('  ', ' ').replace("|", "\n")
        cleaned_header = cleaned_header.split("\n")
        cleaned_header = [s.strip() for s in cleaned_header]

        self.date = cleaned_header[0]
        self.location = cleaned_header[1]
        self.title = cleaned_header[2]
        
    def expand_table(self):
        """
        Waits for the main table to load on the webpage.
        """
        try:
            WebDriverWait(self.driver, MAIN_TABLE_TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, "MainTable"))
            )
            logging.info("Main table loaded.")
        except Exception as e:
            logging.error(f"Error waiting for main table: {e}")

    def get_table_as_df(self):
        """
        Extracts a table with the class 'MainTable' from the webpage and returns it as a DataFrame.

        Returns:
            pd.DataFrame: The extracted table as a pandas DataFrame.
        """
        table = self.soup.find("table", {"class": "MainTable"})
        if not table:
            logging.warning("No table found with class 'MainTable'.")
            return pd.DataFrame()

        # Extract column headers
        header_cols = table.find("thead").find_all("th")
        columns = [th.text.strip() for th in header_cols][1:-1]
        if not columns:
            logging.warning("No columns found in the table.")
            return pd.DataFrame()

        # Create an empty DataFrame
        df = pd.DataFrame(columns=columns)

        # Extract rows
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if cols:
                values = [col.text.strip() for col in cols][1:-1]
                df.loc[len(df)] = values

        self.dataFrame = df

    def close(self):
        """
        Closes the WebDriver.
        """
        if self.driver:
            self.driver.quit()
            logging.info("Driver closed.")


    def normalize_time(self, time_str,):
        """
        Makes sure that string is in format HH:MM:SS

            Parameters: 
                time_str: String describing the time 
        """

        time_parts = time_str.split(":")
        if len(time_parts) == 2:
            time_str = f"00:{time_str}"  # Add "00:" for hours
        return time_str
    
    def set_time(self): 
        """
        Converts the string displaying the time to a timedelta object; then computes the time in minutes
        """
        self.dataFrame["datetime"] = self.dataFrame["Zeit"].apply(self.normalize_time)
        self.dataFrame["datetime"] = pd.to_datetime(self.dataFrame["datetime"])
        self.dataFrame["Zeit"] = self.dataFrame["datetime"].dt.strftime("%H:%M:%S")
        #self.dataFrame["Zeit_minutes"] = self.dataFrame["Zeit"].dt.total_seconds() / 60
        #self.dataFrame["Zeit"] = self.dataFrame["Zeit"].dt.components.apply(lambda row: f"{row.hours:02}:{row.minutes:02}:{row.seconds:02}", axis=1)
    
    def set_agegroup(self): 
        """
        extracts the ageroup form the AK-Pl. col
        """
        pattern = r"^\d+\.\s*(.*)"
        self.dataFrame["AK"] = self.dataFrame["AK-Pl."].apply(lambda x: re.sub(pattern, r"\1", x))
    
    def set_sex(self): 
        """
        sets the sex
        """
        self.dataFrame["M/W"] = self.dataFrame["AK"].str[0]
    
    def drop_nat(self): 
        self.dataFrame.drop(["Nat."], axis=1, inplace=True)
            
    def scrape_data(self, url):
        """
        Performs all necessary steps to scrape data from the given URL:
        - Sets the source URL
        - Handles cookie banner
        - Retrieves metadata
        - Clicks 'Show All' buttons
        - Expands the table
        - Extracts data as a DataFrame
        
        Args:
            url (str): The URL to scrape data from.
        
        Returns:
            dict: A dictionary containing:
                - 'metadata': A dictionary with 'date', 'location', and 'title'
                - 'data': A pandas DataFrame with the extracted table
        """

        # Step 1: Set the source
        self.set_source(url)

        # Step 2: Handle the cookie banner
        self.handle_cookie_banner()

        self.click_show_all_buttons()

        # Step 3: Get the metadata about the race
        self.create_soup()

        self.get_metadata()

        # Step 4: Click 'Show All' buttons if any


        # Step 5: Expand the table
        self.expand_table()

        # Step 6: Get the data as a DataFrame
        self.get_table_as_df() 

        self.set_time()

        self.set_agegroup() 

        self.set_sex() 

        self.drop_nat()

        self.close() 

        return self.dataFrame




