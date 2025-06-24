# Installing necessary modules
# pip install -qU "langchain[google-genai]" langchain-openai langchain-core langgraph langchain-community beautifulsoup4 playwright dotenv 

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
import ast
from playwright.sync_api import sync_playwright
import time
import requests

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

# Setting up currently logged in user and capturing the User ID
USER_ID = 9 # 9 is for testing purposes only. The actual user ID will be gotted when user clicks the "Ok" button in the desktop app
SELECTED_OPTION = "Chailease"
SELECTED_LOAN = "Chailease"
CHAILEASE_URL = "https://e-submission.chailease.com.my/" # Dashboard URL
LOGING_PAGE = "https://e-submission.chailease.com.my/login"
SUBMISSION_PAGE = "https://e-submission.chailease.com.my/submission"
FORM_URL = url = f"https://e-submission.chailease.com.my/apply?actionType=new&submissionNo=0&companyId={USER_ID}2&disableConvertUrl=true&lending=H&productCode=H-007-0000&productName=HP%20for%20Super%20Bike%20-%20New&productType=007"

# Querrying the DB to get login details to use at https://e-submission.chailease.com.my/login
login_details = db.run(f"""
     SELECT ID, AccountName, Password FROM LoanAccounts WHERE ID = {USER_ID};
""")
login_credentials = db_chain.invoke(login_details)
print(login_credentials)
credentials_result = login_credentials

# Getting the actual USser Account and Password for Login
results = credentials_result["input"]
# Convert string of database output to actual list
id = ast.literal_eval(results)[0][0]
username = ast.literal_eval(results)[0][1]
password = ast.literal_eval(results)[0][2]

#reCAPTCHA with Playwright. Playwright is light and Faster than Selenium. Changed to Playwright + Requests + BeautifulSoup 
from playwright.sync_api import sync_playwright
import time
import requests

# ---  LOGIN Page with reCAPTCHA ---
def login(username, password):

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://e-submission.chailease.com.my/login")

        page.fill("#account", username)
        page.fill("#userPassword", password)

        # Wait for iframe with reCAPTCHA
        iframe_element = page.frame_locator("iframe[src*='recaptcha']")
        iframe = iframe_element.frame()

        # Click on the checkbox inside the iframe
        iframe.locator("#ngrecaptcha-0").click()

        # Optional: wait and observe
        page.wait_for_timeout(3000)

        cookies = context.cookies()

    print("Login Successfull")  

# Python code to convert database output to Python Dictionary
def parse_to_dict(text: str) -> dict:
    data = {}
    lines = text.strip().splitlines()
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            value = value.strip()
            # Convert values
            if value.lower() == "none":
                value = None
            elif value.isdigit():
                value = int(value)
            data[key.strip()] = value
    return data
  

# ----   Page 1/7 ---
#After Login, the following is the submission page ---
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
    page.get_by_label("ID No").fill(f"{USER_ID}")

    # === Step 4: Click Next
    page.get_by_role("button", name="Next").click()
    page.wait_for_timeout(3000)

    # === Step 5: Fill Personal Info table fields
    for field, value in personal_info_data.items():
        try:
            page.get_by_label(field).fill(str(value))
        except:
            print(f"[WARN] Could not fill: {field}")

    print("First Submission!.")

# Fetch data from Personal Info table for User ID {USER_ID}
query = f"""
  SELECT "Address", "Bumi", "Email", "Gender", "ID", "Loan Status", "Marital Status",
        "Name", "No of year in residence", "NRIC", "Ownership Status", "Phone Number",
        "Race", "Stay in registered address", "Timestamp", "Title",
        "Where user stay(If not stay in registered address)"
  FROM "Personal Info"
WHERE ID = {USER_ID}
"""
db_result = db_chain.run(query)
personal_info = parse_to_dict(db_result)

def fill_application_form(context, personal_info):
    page = context.new_page()
    page.goto(FORM_URL)
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

    print("Personal Info filled successfully.")


# ---  Employment Data Page 2/7 ---

#Getting Employment Info from Database
# Fetch Working Info where ID = USER_ID
query = f"""
SELECT * FROM "Working Info" WHERE ID = {USER_ID}
"""
working_info_raw = db_chain.run(query)
working_info = parse_to_dict(working_info_raw)
print(working_info)

def fill_working_info_form(context, working_info):
    page = context.pages
    page.goto(FORM_URL)

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
def skip_guarantor_page(page):
    page.goto(FORM_URL)
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


# -- Reference Contact Query Page 4/7 ---
# Fetch Working Info where ID = USER_ID
query = f"""
SELECT * FROM "Reference Contact" WHERE NRIC = {USER_ID}
"""
ref = db_chain.run(query)
