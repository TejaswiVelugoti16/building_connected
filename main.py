import os
import json
import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
'''
User input for query... 
We can give the company name directly or 
we can mention the alphabet to get the company names with those alphabets then
we get the company details related to the query

'''
search_query = input("🔍 Enter a search letter or keyword (e.g., a, b, new): ").strip()

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
print("[🌐] Login page opened.")
print("[🔐] log in manually (Autodesk + 2FA) and select your company.")
input("✅ Press Enter once you reach the 'What's the name of your company?' screen...")

#Step 2: Extract cookies and make the API call
print("[🍪] Extracting session cookies...")
session = requests.Session()
for cookie in driver.get_cookies():
    session.cookies.set(cookie['name'], cookie['value'])

headers = {
    "User-Agent": ua.random,
    "Accept": "application/json"
}

# Step 3: Query API which provides json data related to the companies
from_index = 0 # By scrolling down the from value is increased by 20 for now to provide the sample output just provided it as 0
url = f"https://app.buildingconnected.com/api/searchv3/welcome-flow/?query={search_query}&coords%5Blat%5D=37.7833&coords%5Blng%5D=-122.4167&from={from_index}"
print(f"[🔗] Fetching data from: {url}")
response = session.get(url, headers=headers)

# Step 4: Save data
if response.status_code == 200:
    data = response.json()
    os.makedirs("output", exist_ok=True)

    flat_data = []
    for item in data.get("hits", []):
        flat_data.append({
            "CompanyName": item.get("companyName"),
            "EmployeeCount": item.get("employeesCount", 0),
            "Locations": item.get("offices", []),
            "phone": item.get("phone"),
            "Fax": item.get("fax")
        })

    if flat_data:
        #Save data in csv format
        with open("output/data.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
            writer.writeheader()
            writer.writerows(flat_data)
        
        #save data in json format
        with open("output/data.json", "w") as f:
            json.dump(flat_data, f, indent=2)

        print(f"[✅] Saved {len(flat_data)} results to 'output/company_data.csv'")
    else:
        print("[⚠️] No results found.")
else:
    print(f"[❌] API request failed: {response.status_code} - {response.text}")

# Close browser
driver.quit()
