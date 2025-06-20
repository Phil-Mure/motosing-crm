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

=== CAPTCHA SOLVER ===

def solve_recaptcha(site_key, page_url, api_key): url = "http://2captcha.com/in.php" payload = { "key": api_key, "method": "userrecaptcha", "googlekey": site_key, "pageurl": page_url, "json": 1 } response = requests.post(url, data=payload) request_id = response.json().get("request")

fetch_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
while True:
    time.sleep(5)
    result = requests.get(fetch_url)
    if result.json()["status"] == 1:
        return result.json()["request"]
    elif "CAPCHA_NOT_READY" in result.text:
        continue
    else:
        raise Exception("Captcha solving failed: " + result.text)

=== SELENIUM SETUP ===

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)


=== LOGIN TO CHAILEASE ===

username = credentials_result.split("username": ")[1].split(",")[0].strip("' \n")
password = credentials_result.split("password": ")[1].split("\n")[0].strip("' \n")

# === CAPTCHA SOLVER ===
def solve_recaptcha(site_key, page_url, api_key):
    url = "http://2captcha.com/in.php"
    payload = {
        "key": api_key,
        "method": "userrecaptcha",
        "googlekey": site_key,
        "pageurl": page_url,
        "json": 1
    }
    response = requests.post(url, data=payload)
    request_id = response.json().get("request")

    fetch_url = f"http://2captcha.com/res.php?key={api_key}&action=get&id={request_id}&json=1"
    while True:
        time.sleep(5)
        result = requests.get(fetch_url)
        if result.json()["status"] == 1:
            return result.json()["request"]
        elif "CAPCHA_NOT_READY" in result.text:
            continue
        else:
            raise Exception("Captcha solving failed: " + result.text)

# === SELENIUM SETUP ===
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

# === LOGIN AND SUBMIT ===
driver.get(CHAILEASE_URL)

driver.find_element(By.ID, "username").send_keys(username)
driver.find_element(By.ID, "password").send_keys(password)

captcha_token = solve_recaptcha(SITE_KEY, CHAILEASE_URL, CAPTCHA_API_KEY)
driver.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML = "{captcha_token}";')

driver.find_element(By.ID, "loginBtn").click()
time.sleep(5)


