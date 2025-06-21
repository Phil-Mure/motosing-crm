# Installing necessary modules
# pip install -qU "langchain[google-genai]" langchain-openai langchain-core langgraph langchain-community beautifulsoup4

# Importing necessary modules
import faiss
import bs4
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing_extensions import List, TypedDict

import getpass
import os

if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

from langchain.chat_models import init_chat_model

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
import getpass
import os

if not os.environ.get("GOOGLE_API_KEY"):
  os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


embedding_dim = len(embeddings.embed_query("hello world"))
index = faiss.IndexFlatL2(embedding_dim)

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

os.environ["LANGSMITH_TRACING"] = "true"
if not os.environ.get("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass()



#Initializing the database 
db = SQLDatabase.from_uri("mysql+mysqlconnector://root:FQfC$peBp_^2Y2L@178.128.49.31:3306/crm_002_db")
print(db.dialect)
print(db.get_usable_table_names())

#Create SQL Chain
db_chain = create_sql_agent(llm=llm, db=db, agent_type="openai-tools", verbose=True)

#
login_details = db.run("""
    SELECT ID, AccountName, Password FROM LoanAccounts;
""")


#Getting site pages
page0 = "https://e-submission.chailease.com.my/"
page1 = "https://e-submission.chailease.com.my/"
page2 = "https://e-submission.chailease.com.my/submission"


#Getting login details 
USER_ID = 9
SELECTED_OPTION = "Loan Status"
SELECTED_LOAN = "Chailease"
CHAILEASE_URL = "https://e-submission.chailease.com.my/"
SITE_KEY = "not yet rotten this"  # replace with actual site key
CAPTCHA_API_KEY = "not yet gotten this"

credentials_query = login_details

username = credentials_result.split("AccountName": ")[1].split(",")[0].strip("' \n") 
password = credentials_result.split("Password": ")[1].split("\n")[0].strip("' \n")


#reCAPTCHA with Playwright. Playwright is light and Faster than Selenium. Changed to Playwright + Requests + BeautifulSoup 
from playwright.sync_api import sync_playwright
import time
import requests

def solve_captcha_2captcha(site_key, page_url, api_key):
    url = "http://2captcha.com/in.php"
    payload = {
        "key": api_key,
        "method": "userrecaptcha",
        "googlekey": site_key,
        "pageurl": page_url,
        "json": 1
    }
    res = requests.post(url, data=payload).json()
    request_id = res["request"]

    fetch_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
    while True:
        time.sleep(5)
        result = requests.get(fetch_url).json()
        if result["status"] == 1:
            return result["request"]
        elif result["request"] != "CAPCHA_NOT_READY":
            raise Exception(result["request"])

def login_and_get_cookies(username, password, sitekey, captcha_key):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://e-submission.chailease.com.my/")

        page.fill("#username", username)
        page.fill("#password", password)

        token = solve_captcha_2captcha(sitekey, "https://e-submission.chailease.com.my/", captcha_key)
        page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML = "{token}"')
        page.click("#loginBtn")

        page.wait_for_timeout(3000)
        cookies = context.cookies()
        browser.close()
        return cookies

#Storing login cookies and session with  requests and BeautifulSoup 
import requests
from bs4 import BeautifulSoup

def use_cookies_with_requests(cookies):
    session = requests.Session()
    for c in cookies:
        session.cookies.set(c['name'], c['value'])

    dashboard = session.get("https://e-submission.chailease.com.my")
    soup = BeautifulSoup(dashboard.text, "html.parser")

    # example: find form and fill it
    loan_form = soup.find("form", {"id": "loan_form"})
    print("Form found:", bool(loan_form))


#Page 1/7
#---After Login, the following is the submission page ---
from playwright.sync_api import sync_playwright
import time

def fill_submission_form(context, personal_info_data):
    page = context.new_page()
    page.goto("https://e-submission.chailease.com.my/submission")
    time.sleep(3)

    # === Step 1: Select radio with value="new"
    page.locator('input[name="action"][value="new"]').check()

    # === Step 2: Select dropdown with "HP for Super - New"
    dropdown = page.locator('select.ng-tns-c77-16')
    dropdown.select_option(label="HP for Super - New")

    # === Step 3: Fill ID No
    page.get_by_label("ID No").fill("9")

    # === Step 4: Click Next
    page.get_by_role("button", name="Next").click()
    page.wait_for_timeout(3000)

 #---After Submission, the following is the personal infor page ---
# Fetch data from Personal Info table for User ID 16
query = """
SELECT "Address", "Bumi", "Email", "Gender", "ID", "Loan Status", "Marital Status",
       "Name", "No of year in residence", "NRIC", "Ownership Status", "Phone Number",
       "Race", "Stay in registered address", "Timestamp", "Title",
       "Where user stay(If not stay in registered address)"
FROM "Personal Info"
WHERE ID = 16
"""

result = db_chain.run(query)
personal_info = json.loads(result) if isinstance(result, str) else result

#--- Playwright Automation with Personal Info Page----

def fill_application_form(context, personal_info):
    page = context.new_page()
    page.goto("https://e-submission.chailease.com.my/apply?actionType=new&submissionNo=0&companyId=92&disableConvertUrl=true&lending=H&productCode=H-007-0000&productName=HP%20for%20Super%20Bike%20-%20New&productType=007")
    page.wait_for_timeout(3000)

    # Map DB fields to formcontrolnames
    field_map = {
        "idNo": personal_info.get("NRIC"),
        "firstname": personal_info.get("Name"),
        "gender": personal_info.get("Gender"),
        "email": personal_info.get("Email"),
        "mobileNo": personal_info.get("Phone Number"),
        "residentialAddress": personal_info.get("Address"),
        "race": personal_info.get("Race"),
        "maritalStatus": personal_info.get("Marital Status"),
        "ownershipStatus": personal_info.get("Ownership Status"),
        "yearOfStay": personal_info.get("No of year in residence"),
        "stayInRegisteredAddress": personal_info.get("Stay in registered address"),
        "altStayAddress": personal_info.get("Where user stay(If not stay in registered address)"),
        "isBumiputera": personal_info.get("Bumi"),
        "title": personal_info.get("Title")
    }

    # Fill all matching fields
    for control_name, value in field_map.items():
        try:
            if value is not None:
                page.locator(f'[formcontrolname="{control_name}"]').fill(str(value))
        except Exception as e:
            print(f"[WARN] Could not fill {control_name}: {e}")

    print("[INFO] Application form filled successfully.")

# This should be added after login 
fill_submission_form(context, personal_info)  # Step 1 page
fill_application_form(context, personal_info)  # Step 2 page




# Employment Data Page 2/7,
url = https://e-submission.chailease.com.my/apply?actionType=new&submissionNo=0&companyId=92&disableConvertUrl=true&lending=H&productCode=H-007-0000&productName=HP%20for%20Super%20Bike%20-%20New&productType=007

#Getting Employment Info from Database
# Fetch Working Info where NRIC = '980803035298'
query = """
SELECT * FROM "Working Info" WHERE NRIC = '980803035298'
"""
working_info_raw = db_chain.run(query)
working_info = json.loads(working_info_raw) if isinstance(working_info_raw, str) else working_info_raw

def fill_working_info_form(context, working_info):
    page = context.pages[-1]  # Continue on the same page

    # 1. Occupation (Position)
    if working_info.get("Position"):
        page.locator('#occupation').click()
        page.locator(f'text="{working_info["Position"]}"').click()

    # 2. Employer Name
    if working_info.get("Company Name"):
        page.locator('input[name="employerName"]').fill(working_info["Company Name"])

    # 3. Monthly Income
    if working_info.get("Net Salary"):
        page.get_by_label("Monthly Income").fill(str(working_info["Net Salary"]))

    # 4. Work Address
    if working_info.get("Company Address"):
        page.get_by_label("Work Address").fill(working_info["Company Address"])

    # 5. Work Phone No.
    if working_info.get("Company Phone Number"):
        page.get_by_label("Work Phone No.").fill(working_info["Company Phone Number"])

    # 6. Working in Singapore radio button
    if working_info.get("Working in Singapore"):
        answer = str(working_info["Working in Singapore"]).strip().lower()
        if "yes" in answer or "true" in answer or answer == "1":
            page.locator('input[name="workInSingapore"][value="true"]').check()
        elif "no" in answer or answer == "0":
            page.locator('input[name="workInSingapore"][value="false"]').check()

    print("[INFO] Working Info section filled.")

#Skip the Guarantor
page = https://e-submission.chailease.com.my/apply?actionType=new&submissionNo=0&companyId=92&disableConvertUrl=true&lending=H&productCode=H-007-0000&productName=HP%20for%20Super%20Bike%20-%20New&productType=007
def skip_guarantor_page(page):
    try:
        # Try clicking the "Next" or "Skip" button
        page.get_by_role("button", name="Next").click()
        page.wait_for_timeout(2000)
        print("[INFO] Skipped Guarantor page using 'Next' button.")
    except:
        try:
            page.get_by_role("button", name="Skip").click()
            page.wait_for_timeout(2000)
            print("[INFO] Skipped Guarantor page using 'Skip' button.")
        except Exception as e:
            print(f"[WARN] Could not skip Guarantor page: {e}")


#Reference Contact Query Page 4/7
# Fetch Working Info where NRIC = '980803035298'
query = """
SELECT * FROM "Reference Contact" WHERE NRIC = '980803035298'
"""
ref = db_chain.run(query)
ref
#working_info = json.loads(working_info_raw) if isinstance(working_info_raw, str) else working_info_raw


#Filling Reference form
def fill_reference_contact_form(page, ref_contact):
    try:
        if ref_contact.get("Name"):
            page.locator('[formcontrolname="firstName"]').fill(ref_contact["Name"])

        if ref_contact.get("Phone Number"):
            page.locator('[formcontrolname="mobilePhone"]').fill(ref_contact["Phone Number"])

        if ref_contact.get("Relation to user"):
            # Click and select value from dropdown (PrimeNG)
            page.locator('[formcontrolname="relationship"]').click()
            page.locator(f'text="{ref_contact["Relation to user"]}"').click()

        print("[INFO] Reference Contact form filled.")
    except Exception as e:
        print(f"[ERROR] Could not fill Reference Contact section: {e}")
fill_reference_contact_form(page, ref_contact)



#Page 5/7: Collateral
# Get product info for given NRIC
product_query = """
SELECT "Brand", "Down Payment", "ID", "Model", "NRIC", "Number Plate", "Price", "Product Type", "Tenure"
FROM "Product Info"
WHERE NRIC = '980803035298'
"""
product_info_raw = db_chain.run(product_query)
product_info = json.loads(product_info_raw) if isinstance(product_info_raw, str) else product_info_raw

# Get corresponding model from Model Map
model_query = f"""
SELECT "Chailease" FROM "Model Map" WHERE "Webform" = '{product_info.get("Model")}'
"""
model_result = db_chain.run(model_query)
model_name = json.loads(model_result).get("chailease") if isinstance(model_result, str) else model_result.get("chailease")

# If no model is found, raise and stop
if not model_name:
    print("AUTOMATION STOPS NOW - INCORRECT/NON-EXISTING MODEL")
    raise Exception(f"No model found for Webform Model: {product_info.get('Model')}")


def fill_product_info_form(context, product_info, model_name):
    page = context.pages[-1]  # continue on current page

    # 1. Select brand from dropdown
    if product_info.get("Brand"):
        page.locator('[formcontrolname="brand"]').click()
        page.locator(f'text="{product_info["Brand"]}"').click()

    # 2. Select model from mapped Chailease model
    if model_name:
        page.locator('[formcontrolname="model"]').click()
        page.locator(f'text="{model_name}"').click()

    # 3. Date of Manufacture (hardcoded or from DB)
    page.get_by_label("Date of Manufacture").fill("012025")

    # 4. Plate No
    if product_info.get("Number Plate"):
        page.get_by_label("Plate No.").fill(product_info["Number Plate"])

    # 5. Purchase Price
    if product_info.get("Price"):
        page.get_by_label("Purchase Price").fill(str(product_info["Price"]))

    # 6. Down Payment
    if product_info.get("Down Payment"):
        page.get_by_label("Down Payment").fill(str(product_info["Down Payment"]))

    print("[INFO] Product Info section filled successfully.")

fill_product_info_form(context, product_info, model_name)


#Page 6/7 Terms and Conditions
product_query = """
SELECT "Brand", "Down Payment", "ID", "Model", "NRIC", "Number Plate", "Price", "Product Type", "Tenure"
FROM "Product Info"
WHERE NRIC = '980803035298'
"""
product_info_raw = db_chain.run(product_query)
product_info = json.loads(product_info_raw) if isinstance(product_info_raw, str) else product_info_raw


def fill_dealer_and_tenure_fields(context, product_info):
    page = context.pages[-1]

    # 1. Dealer Sales (p-dropdown[formcontrolname="dealerSalesId"])
    page.locator('[formcontrolname="dealerSalesId"]').click()
    page.locator('text="MOTOSING SDN BHD"').click()

    # 2. Marketing Officer - Select First Option
    page.locator('[formcontrolname="marketingOfficer"]').click()
    page.locator('.p-dropdown-item').nth(0).click()

    # 3. Tenure Month from Product Info
    if product_info.get("Tenure"):
        page.locator('[formcontrolname="tenureMonth"]').click()
        page.locator(f'text="{str(product_info["Tenure"])}"').click()

    print("[INFO] Dealer, Marketing Officer and Tenure fields filled.")

fill_product_info_form(context, product_info, model_name)
fill_dealer_and_tenure_fields(context, product_info)