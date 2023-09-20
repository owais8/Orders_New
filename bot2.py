from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import mysql.connector
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException,TimeoutException
import pickle
    
def main():
    
    options=Options()

    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    url = "https://www.psacard.com"
    driver.get(url)

    driver.delete_all_cookies()

    path='cookies2.pkl'
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
    url = "https://www.psacard.com/myaccount/myorders"
    driver.get(url)
    db_config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'psa'
    }
    # Connect to the database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT submission, status FROM orders WHERE status != 'Complete'")
    orders = cursor.fetchall()
    new_status=""
    for submission, status in orders:
        wait = WebDriverWait(driver, 10)

        wait.until(EC.visibility_of_element_located((By.ID, 'search')))
        search_box = driver.find_element(By.ID,"search")  # Replace "q" with the actual attribute value of the search box

        search_box.clear()
        search_box.click()
        search_text = str(submission)
        search_box.send_keys(search_text)
        print(submission)
        # Submit the search by pressing the Enter key
        search_box.send_keys(Keys.RETURN)
        wait = WebDriverWait(driver, 20)
        wait.until(
            lambda driver: driver.current_url != 'https://www.psacard.com/myaccount/myorders')
        wait = WebDriverWait(driver, 20)
        wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div/main')))
        ele=driver.find_elements(By.TAG_NAME,'ul')
        a=ele[9].find_elements(By.CLASS_NAME,"text-primary-500")
        if len(a)<1:
            ele=driver.find_elements(By.TAG_NAME,'ul')
            a=ele[9].find_elements(By.CLASS_NAME,"text-neutral2")
            new_status=a[-1].text
        else:
            new_status=a[-1].text
        driver.back()
        print(new_status)
        if new_status != status:
            update_query = "UPDATE orders SET status = %s WHERE submission = %s"
            update_values = (new_status, submission)
            cursor.execute(update_query, update_values)
            connection.commit()
            
    cursor.close()
    connection.close()
    driver.close()

if __name__ == '__main__':
    main()




    