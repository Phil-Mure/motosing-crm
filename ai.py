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