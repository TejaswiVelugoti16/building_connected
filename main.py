import os
import json
import csv
import random
import re
import time
import requests
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
'''
User input for query... 
We can give the company name directly or 
we can mention the alphabet to get the company names with those alphabets then
we get the company details related to the query

'''


# Set up Chrome with Selenium
ua = UserAgent()
chrome_options = Options()
chrome_options.add_argument(f"user-agent={ua.random}")
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# Step 1: Open Login Page
driver.get("https://app.buildingconnected.com/login?retUrl=%2F")
print(" Login page opened.")
print(" log in manually (Autodesk + 2FA) and select your company.")
time.sleep(10)

expected_text = "What's the name of your company?"
WebDriverWait(driver, 200).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "h2"), expected_text)
    )
time.sleep(10)
driver.get(driver.current_url)
flat_data = []
print(driver.current_url)
time.sleep(5)
for request in driver.requests:
    # Step 3: Query API which provides json data related to the companies
    if request.response and "searchv3/welcome-flow" in request.url:
        print(" Found API Request:")
        #Step 2: Extract cookies and make the API call
        print(" Extracting session cookies...")
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        headers = {
            "User-Agent": ua.random,
            "Accept": "application/json"
        }
        print("URL:", request.url)
        url = request.url
        search_query = re.search(r"[?&]query=([^&]+)", url).group(1)
        print(f"Fetching data from: {url}")
        time.sleep(20)
        response = session.get(url, headers=headers)

        # Step 4: Save data
        if response.status_code == 200:
            data = response.json()
            os.makedirs("output", exist_ok=True)

            for item in data.get("hits", []):
                flat_data.append({
                    "CompanyName": item.get("companyName"),
                    "EmployeeCount": item.get("employeesCount", 0),
                    "Locations": item.get("offices", []),
                    "phone": item.get("phone"),
                    "Fax": item.get("fax")
                })

                delay = random.uniform(2, 5)
                print(f"Sleeping for {delay:.2f} seconds...")
                time.sleep(delay)
        else:
            print(f"API request failed: {response.status_code} - {response.text}")
if flat_data != []:
    #Save data in csv format
    with open(f"output/{search_query}_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
        writer.writeheader()
        writer.writerows(flat_data)
                        
    #save data in json format
    with open(f"output/{search_query}_data.json", "w") as f:
        json.dump(flat_data, f, indent=2)

    print(f"Saved {len(flat_data)} results to 'output/company_data.csv'")
    # Close browser
    driver.quit()

else:
    print("No data found")
