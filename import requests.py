from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def enter_text(field, text): 
    try:
        text_field = driver.find_element(By.XPATH, field) 
        text_field.send_keys(text)  
        print("Text erfolgreich eingegeben.")
    except Exception as e:
        print(f"Fehler beim Eingeben des Textes: {e}")

def handle_cookies():
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "_a9_1")) 
        ).click()
        print("Cookie-Banner geschlossen.")
    except Exception as e:
        print(f"Kein Cookie-Banner gefunden oder Fehler aufgetreten: {e}")


options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get("https://www.instagram.com")

time.sleep(1)

handle_cookies()

time.sleep(1)

name = "janik_wahrheit"
pw = "_KxMxL_131201_"

enter_text('//*[@id="loginForm"]/div/div[1]/div/label/input', name)
enter_text('//*[@id="loginForm"]/div/div[2]/div/label/input', pw)

driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[3]/button').click()
