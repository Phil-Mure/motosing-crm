import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as EdgeService
from selenium.common.exceptions import NoSuchElementException
from selenium_recaptcha_solver import RecaptchaSolver
from selenium_recaptcha_solver import RecaptchaException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
import re
import os
import random
import requests
import pymysql
import zipfile
import sys
# from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from Automation.utils.sftp import retrieveFile 
from Automation.utils.sqlErrorLogging import errorLogging 
from Automation.utils.util import kill_processes 
from Automation.utils.util import get_credentials 
from Automation.utils.util import get_database 
import traceback
import warnings
from Automation.utils.VaultConfig import getVaultData
import asyncio

loop = asyncio.get_event_loop()
vault_client = loop.run_until_complete(getVaultData())
warnings.filterwarnings('ignore',category=UserWarning, message ="pandas only supports SQLAlchemy connectable")

def errorlog(description, stacktrace, filepath):
    try:
        errorLogging('Script : Chailease Automation',  description=description, stacktrace=stacktrace, filepath=filepath)
    except Exception as e:
        print(str(e))

def clearInput(webelement):
    try:
        webelement.send_keys(Keys.CONTROL + "a")
        webelement.send_keys(Keys.DELETE)
    except NoSuchElementException:
        print("Unable to clear input field")
        pass

def get_location_by_postcode(postcode):
    url = f"https://postcode.my/search/?keyword={postcode}&state="
    response = requests.get(url)
    if response.status_code == 200:
        html = response.text
        # Extract the location from the HTML using regular expressions
        match = re.findall(r'<td[^>]*><strong><a[^>]*>([^<]*)</a>', html)
        match1 = re.search(r'<td[^>]*><strong><a[^>]*>([^<]*)</a>', html)
        if match[1] == 'Wilayah Persekutuan':
            print("From API :",[f"{match[1]} {match[0]}", match1.group(1)])
            return [f"{match[1]} {match[0]}", match1.group(1)]
        if match and match1:
            print("From API :",[match[1], match1.group(1)])
            return [match[1], match1.group(1)]
    return None

# vault
# Reading a secret
dbip, dbusername, dbpassword, dbport = vault_client['ip'], vault_client['username'], vault_client['password'], vault_client['port']
dbport = int(dbport)
try:
    cnx = pymysql.connect(
        host= dbip,
        user= dbusername,
        password= dbpassword,
        database=get_database(sys.argv[3]),
        port= dbport
    )

    # might need to change user agent from time to time
    user_agent = [
        'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'
    ]
    random_user_agent = user_agent[random.randint(0,len(user_agent) - 1)]
    print("User-agent : ", random_user_agent)
    # options.add_argument(f'--user-agent={random_user_agent}')
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        latest_version = EdgeChromiumDriverManager().driver.get_latest_release_version()
        print("Latest version:", latest_version)
        driver_notes_path = rf'C:\Users\user\.wdm\drivers\edgedriver\win64\{latest_version}\Driver_Notes'
        if os.path.exists(driver_notes_path):
            shutil.rmtree(driver_notes_path)
            

        driver_path = rf'C:\Users\user\.wdm\drivers\edgedriver\win64\{latest_version}\msedgedriver.exe'
        # kill all msedgedriver processes
        kill_processes('msedgedriver.exe')
        if os.path.exists(driver_path):
            os.remove(driver_path)
    except Exception as e:
        pass


    options = webdriver.EdgeOptions()
    options.add_argument(f'--user-agent={random_user_agent}')
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    # driver = webdriver.Chrome(service=service, options=options)
    
    wait = WebDriverWait(driver, 10)

    solver = RecaptchaSolver(driver)

    driver.get("https://e-submission.chailease.com.my/")
    sleep(random.randint(3, 5))
    print("Running")
    scroll_amount = random.randint(100, 500)
    driver.execute_script("window.scrollTo(0, " + str(scroll_amount) + ");")
    sleep(random.randint(1, 3))
    
    username , password = get_credentials(sys.argv[2], sys.argv[3])
    nric = sys.argv[1]
        
    print("NRIC :",nric)

    # Username and Password
    driver.find_element(
        By.CSS_SELECTOR, '.login-input-ac'
        # By.XPATH, "//*[@id='account']"
    ).send_keys(username)
    driver.find_element(
        By.CSS_SELECTOR, '.login-input-pw'
        # By.XPATH, "//*[@id='userPassword']"
    ).send_keys(password)
    sleep(1)

    #if recaptcha fail, try another user agent, or try exploring proxies
    print("Doing Recaptcha")
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1} to solve reCAPTCHA...")

            # Find the reCAPTCHA iframe without switching into it manually
            recaptcha = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]'))
            )

            # Call the solver using the iframe directly
            solver.click_recaptcha_v2(iframe=recaptcha)

            print("Done Recaptcha")
            break  # Success — exit loop

        except (RecaptchaException, TimeoutException, NoSuchElementException) as e:
            filename = f"{nric}_Chailease_Recaptcha_Attempt{attempt+1}.png"
            driver.save_screenshot(filename)
            errorlog(f'Recaptcha attempt {attempt + 1} failed: {e}', traceback.format_exc(), filename)
            print(f"Recaptcha failed on attempt {attempt + 1}.", file=sys.stderr)

            if attempt == max_attempts - 1:
                raise Exception("Recaptcha failed after multiple attempts.")
            else:
                print("Retrying Recaptcha...")
                sleep(2)

    

    try:
        # Log In
        driver.find_element(
            By.CSS_SELECTOR, '.btn-login'
            # By.XPATH, "/html/body/app-root/div[1]/app-login/div/main/div/div[2]/form/div[5]/div/a"
        ).click()
        print("Logged in")
        sleep(8)
        

        # Submission Button
        Submission = 'document.querySelector("body > app-root > div > app-extranet-layout > div > sigv-extranet-side-menu > p-sidebar.ng-tns-c33-10.ng-star-inserted > div > div > div > ul > li:nth-child(1) > a > div").click()'
        #Submission = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > app-side-menu > p-sidebar.ng-tns-c33-12.ng-star-inserted > div > div > div > ul > li:nth-child(1) > a').click()"
        driver.execute_script(Submission)
    except Exception as e:
        filename = f"{nric}_Chailease_Login.png"
        driver.save_screenshot(filename)
        errorlog(f'Error in Login : {e}',traceback.format_exc(), filename)
        print(e, file=sys.stderr)
        raise Exception(e)
    
    try:
        # retrieve the file from sftp script
        retrieveFile(nric, sys.argv[3])
        
        dfProductInfo = pd.read_sql(
            f"SELECT * FROM `Product Info` WHERE NRIC={nric}", cnx)
        print(dfProductInfo)
        
        for i in range(0, len(dfProductInfo)):
            print("New Case Application")
            
            # New Case Application
            sleep(2)
            driver.find_element(
                By.CSS_SELECTOR, 'p-radiobutton[name="action"][ng-reflect-input-id="newCase"]'
                # By.XPATH, "/html/body/app-root/div/app-extranet-layout/div/div/div/app-leading-page/div[1]/div[1]/p-radiobutton/div/div[2]"
            ).click()
            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown[ng-reflect-option-label="productName"]'
                # By.XPATH, "/html/body/app-root/div/app-extranet-layout/div/div/div/app-leading-page/div[1]/div[2]/div/div/p-dropdown/div"
            ).click()
            
            product = dfProductInfo['Product Type'].item().split()
            Product = f"{product[0] + product[-1].split(')')[-1]}"
            
            # print(product)
            # print(Product)
            superbike_new = '//li[contains(@aria-label, "HP for Super Bike - New")]'
            superbike_used =  '//li[contains(@aria-label, "HP for Super Bike - Used")]'
            moped_new =  '//li[contains(@aria-label, "HP for Moped-New")]' 
            moped_rnm =  '//li[contains(@aria-label, "HP for Moped-RNM")]'
            moped_used =  '//li[contains(@aria-label, "HP for Moped-Used")]'

            if Product == "superbikenew" or Product == "bigbikenew":
                driver.find_element(By.XPATH, superbike_new).click()
            elif Product == "superbikeused" or Product == "bigbikeused":
                driver.find_element(By.XPATH, superbike_used).click()
            elif Product == "mopednew" or Product == "scooternew":
                driver.find_element(By.XPATH, moped_new).click()
            elif Product == "mopedrnm" or Product =="scooterrnm":
                driver.find_element(By.XPATH, moped_rnm).click()
            elif Product == "mopedused" or Product == "scooterused":
                driver.find_element(By.XPATH, moped_used).click()
            sleep(2)
        
            # Next Button
            driver.find_element(
                By.XPATH, "/html/body/app-root/div/app-extranet-layout/div/div/div/app-leading-page/div[2]/a").click()
            sleep(5)
            print("Starting Customer Information")
            # Page 1/7 Customer Infomation
            # ID No.(IC)
            data = pd.read_sql(
                f"SELECT * FROM `Personal Info` WHERE NRIC={nric}", cnx)
            driver.find_element(
                By.CSS_SELECTOR, '[formcontrolname="idNo"]'
            ).send_keys(data['NRIC'].item())
            # check for existing input in other fields
            nameElement = driver.find_element(
                By.CSS_SELECTOR, '[formcontrolname="firstName"]'
            )
            nameElement.click()
            sleep(5)
            clearInput(nameElement)
            nameElement.send_keys(data['Name'].item())
            print("Done : Name")
            # Gender
            gender = data['Gender'].item().lower()
            if gender == "male":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-radiobutton[formcontrolname="gender"][ng-reflect-value="1"]'
                ).click()
            elif gender == "female":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-radiobutton[formcontrolname="gender"][ng-reflect-value="2"]'
                ).click()
            sleep(1)
            print("Done : Gender")
            # Nationality
            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown[formcontrolname="nationality"]'
            ).click()
            if len(nric) == 12:
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Citizen"]'
                ).click()
            else:
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Foreigner"]'
                ).click()
            sleep(2)
            print("Done : Nationality")
            # disabling hidden wrapper elements
            hiddenElement = driver.find_element(By.CLASS_NAME, 'cfc-wrapper-bg-gray')
            driver.execute_script("arguments[0].style.pointerEvents = 'none'; arguments[0].style.opacity = '0.5';", hiddenElement)
            hiddenElement = driver.find_element(By.CLASS_NAME,'cfc-common-bottom-panel-wrapper')
            driver.execute_script("arguments[0].style.pointerEvents = 'none'; arguments[0].style.opacity = '0.5';", hiddenElement)
            hiddenElement = driver.find_element(By.CLASS_NAME,'cfc-common-bottom-panel')
            driver.execute_script("arguments[0].style.pointerEvents = 'none'; arguments[0].style.opacity = '0.5';", hiddenElement)
            
            # Race
            malay = 'p-dropdownitem[ng-reflect-label="Malay"]'
            chinese = 'p-dropdownitem[ng-reflect-label="Chinese"]'
            indian = 'p-dropdownitem[ng-reflect-label="Indian"]'
            other = 'p-dropdownitem[ng-reflect-label="Other"]'

            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown[formcontrolname="race"]'
            ).click()
                
            race = data['Race'].item()
            if race.capitalize() == "Malay":
                driver.find_element(By.CSS_SELECTOR, malay).click()
            elif race.capitalize() == "Chinese":
                driver.find_element(By.CSS_SELECTOR, chinese).click()
            elif race.capitalize() == "Indian":
                driver.find_element(By.CSS_SELECTOR, indian).click()
            else:
                driver.find_element(By.CSS_SELECTOR, other).click()
            sleep(1)
            print("Done : Race")
            # Email Address
            emailElement = driver.find_element(
                By.CSS_SELECTOR, 'input[formcontrolname="email"]'
            )
            clearInput(emailElement)
            emailElement.send_keys(data['Email'])
            sleep(3)
            print("Done : Email")
            # reenter address even if there is existing data
            # Reg Address
            address = data['Address'].item()
            postcode = address.split(',')[-3].strip()
            locationArray = get_location_by_postcode(postcode)
         
            # search the sate
            regaddress = 'p-dropdown[class*="addr-level-01"]'
            driver.find_element(By.CSS_SELECTOR,regaddress).click()
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.p-dropdown-filter.p-inputtext.p-component'))).send_keys(locationArray[0])
            # click on the state base on the dropdown element
            dropdownElement = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.p-dropdown-items')))
            driver.find_element(By.CSS_SELECTOR, 'input.p-dropdown-filter.p-inputtext.p-component').send_keys(Keys.ARROW_DOWN)
            stateSpan = dropdownElement.find_element(By.XPATH, f"//span[text()=\"{locationArray[0]}\"]")
            wait.until(EC.element_to_be_clickable(stateSpan)).click()
            print("Done : State")
            sleep(6)

            # Reg Address 2
            # click to open the dropdown
            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown.addr-level-02'
            ).click()
            try:
                # try to find the search input
                sleep(3)
                # Locate the input field within the dropdown and send keys
                dropdownElementdistrict = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.p-dropdown-items')))
                dropdownliElementDistrict = dropdownElementdistrict.find_elements(By.TAG_NAME, 'li')

                for li in dropdownliElementDistrict:
                    if li.text == locationArray[1]:
                        li.click()
                        break
            except TimeoutException:
                print("Dropdown list didn't become visible within the timeout.")
                pass
            except NoSuchElementException:
                print("No such element exception occurred.")
                pass
            print("Done : City")
            sleep(6)
            postcodeSpan = 'p-dropdown[class*="addr-postcode"]'
            driver.find_element(By.CSS_SELECTOR, postcodeSpan).click()
            sleep(3)
            dropdownElementdistrict = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.p-dropdown-items')))
            postcodeSpan = dropdownElementdistrict.find_element(By.XPATH, f"//span[text()=\"{postcode}\"]")
            wait.until(EC.element_to_be_clickable(postcodeSpan)).click()
            if postcodeSpan:
                postcodeSpan.click()
            sleep(3)
            print("Done : postcode")

            address_line = ', '.join(address.split(',')[:-3])
            addressElement1 = driver.find_element(
                By.CSS_SELECTOR, 'input.addr-level-05[placeholder=" Unit/House Number, Street Name, Apartment, Suite"]'
            )
            clearInput(addressElement1)
            addressElement1.send_keys(address_line)
            print("Done : Address")
            
            # Contact Address
            contactaddress = 'button.p-button-secondary[ng-reflect-label="Reg. Add"]'
            driver.find_element(By.CSS_SELECTOR, contactaddress).click()
            print("Done : Contact Address")
            sleep(3)
            # Phone No.
            phoneElement = driver.find_element(
                By.CSS_SELECTOR, 'input[formcontrolname="mobilePhone1"]'
            )
            clearInput(phoneElement)
            phoneElement.send_keys(data['Phone Number'].item()[2:])
            sleep(1)
            print("Done : Phone No.")
            sleep(3)
            print("End Customer Information")
            # Next0
            Next0 = 'document.querySelector("body > app-root > div > app-extranet-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a").click()'
            driver.execute_script(Next0)


            sleep(3)
            print("Start Employement Information")
            # Page 2/7 Employment
            # Occupation
            Factory_Operator_list = ['professional worker','operational worker(assembly line worker)','operational worker(bus drivers)',
                                    'operational worker(carpenters)','operational worker(farm worker)','operational worker(forklift operator)',
                                    'operational worker(hairstylists)','operational worker(machine operator)','operational worker(mechanics)',
                                    'operational worker(quality control inspectors)','operational worker(rig workers)','operational worker(security guards)',
                                    'operational worker(stock clerks)','operational worker(truck drivers)','operational worker(warehouse workers)',]
            Clerical_Staff_list = ['assistant manager','supervisor','general manager','judge',
                                'executives', 'department manager','project manager','operational worker(data entry operators)']
            Promotor_Cashier_Shop_assistant_list = [
                'operational worker(waiters/waitresses)','operational worker(sales associates/promoters)','operational worker(receptionists)',
                'operational worker(cleaners)','operational worker(cashier)','operational worker(dishwashers)']
            Own_business_hawker_list = ['']
            Government_servants_list = ['firefighters','police officer','public transit operators','social workers','military']
            General_Worker_list = ['operational worker(administrative assistants)','operational worker(chef)','operational worker(chef assistants)',
                                'operational worker(construction workers)','operational worker(customer service representatives)',
                                'operational worker(delivery riders/drivers)','operational worker(electricians/plumbers/heavy equipment operators)',
                                'operational worker(housekeeping staff (hotel))','operational worker(lab technicians)','operational worker(lawyers)',
                                'operational worker(medical assistants)','operational worker(medical technicians)','operational worker(nurses)',
                                'operational worker(paramedics)','operational worker(professors)','operational worker(teachers/principal)',
                                'operational worker(volunteer)','operational worker(flight attendants)','operational worker(postman)']

            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown[id="occupation"]'
            ).click()
            
            queryWorkingInfo = f"SELECT * FROM `Working Info` WHERE NRIC = {nric}"
            dfworkingInfo = pd.read_sql(queryWorkingInfo, cnx)
            print(dfworkingInfo)
            
            occupation = dfworkingInfo['Position'].item()
            employmentStatus = dfworkingInfo['Employment Status'].item()

            if employmentStatus == 'self-employed':
                occupationSpan = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, 'li[aria-label="Own business–hawker"]')
                ))
                occupationSpan.click()
            else:
                if occupation in General_Worker_list:
                    occupationSpan = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'li[aria-label="General worker"]')
                    ))
                    occupationSpan.click()

                elif occupation in Factory_Operator_list:
                    occupationSpan = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'li[aria-label="Factory operator"]')
                    ))
                    occupationSpan.click()

                elif occupation in Clerical_Staff_list:
                    occupationSpan = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'li[aria-label="Clerical staff"]')
                    ))
                    occupationSpan.click()

                elif occupation in Promotor_Cashier_Shop_assistant_list:
                    occupationSpan = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'li[aria-label="Promotor/cashier/shop assistant"]')
                    ))
                    occupationSpan.click()

                elif occupation in Government_servants_list:
                    occupationSpan = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'li[aria-label="Government servant"]')
                    ))
                    occupationSpan.click()

                else:
                    occupationSpan = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, 'li[aria-label="Unemployed"]')
                    ))
                    occupationSpan.click()
                sleep(1.5)
            print("Done : Occupation")
            # Employer Name
            employerName = driver.find_element(
                By.CSS_SELECTOR, 'input[name="employerName"]'
            )
            clearInput(employerName)
            employerName.send_keys(dfworkingInfo['Company Name'].item())
            sleep(1)
            print("Done : Employer Name")
            # Monthly Income
            grossSalary = driver.find_element(
                By.XPATH, '/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[2]/div[2]/div[2]/sigv-input-number/span/input'
            )
            clearInput(grossSalary)
            grossSalary.send_keys(dfworkingInfo['Gross Salary'].item()[2::])
            sleep(1)
            print("Done : Monthly Income")
            
            # Work Address
            splitWorkingAddress = dfworkingInfo['Company Address'].item().split(',')
            splitWorkingAddress = [part.strip() for part in splitWorkingAddress]
            print(splitWorkingAddress)
            postcode = splitWorkingAddress[-3]
            work_singapore = False
            if splitWorkingAddress[-1].lower() == 'singapore':
                work_singapore = True
                locationArray = ['Other', 'Other']
                postcode = "Other"
            if not work_singapore:
                locationArray = get_location_by_postcode(postcode)
            driver.find_element(
                By.XPATH,'/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[4]/div/div/div[2]/div[1]/sigv-address-selector/div[1]/div[1]/p-dropdown/div/span'
            ).click()
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.p-dropdown-filter.p-inputtext.p-component'))).send_keys(locationArray[0])
            stateSpan = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.p-dropdown-items li span.ng-star-inserted'))).click()
            print("Done : State")
            sleep(3)
            driver.find_element(
                By.XPATH,'/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[4]/div/div/div[2]/div[1]/sigv-address-selector/div[1]/div[2]/p-dropdown/div/span'
            ).click()
            try:
                # try to find the search input
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input.p-dropdown-filter.p-inputtext.p-component'))).send_keys(locationArray[1])
            except TimeoutException:
                pass
            dropdownElement = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'ul.p-dropdown-items')))
            sleep(2)
            allCity = driver.find_elements(By.CSS_SELECTOR, 'ul.p-dropdown-items span.ng-star-inserted')
            for city in allCity:
                if city.text == locationArray[1]:
                    city.click()
            print("Done : City")
            sleep(3)
            
            driver.find_element(
                By.XPATH,'/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[4]/div/div/div[2]/div[1]/sigv-address-selector/div[2]/div[1]/p-dropdown/div/span'
            ).click()
            try:
                # try to find the search input
                if not work_singapore:
                    postcodeSpan = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'li.p-dropdown-item.p-ripple')))
                    postcodeSpan.click()
                if work_singapore:
                    driver.find_element(By.CSS_SELECTOR, 'li.p-dropdown-item.p-ripple').click()
            except TimeoutException:
                pass

            print("Done : Postcode")
            sleep(3)
            
            fullAddress = ', '.join(splitWorkingAddress[:-3])
            workAddress = driver.find_element(
                By.XPATH,"/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[4]/app-employment/div/form/div[4]/div/div/div[2]/div[1]/sigv-address-selector/div[2]/div[2]/input"
            )
            clearInput(workAddress)
            workAddress.send_keys(fullAddress)
            print("Done : Company Address")
            sleep(2)
            
            # Work Phone No.
            workPhoneNo = driver.find_element(
                By.CSS_SELECTOR, 'input[name="workPhone"]'
            )
            clearInput(workPhoneNo)
            workPhoneNo.send_keys(dfworkingInfo['Company Phone Number'].item())
            sleep(1)
            print("Done : Company Phone number")

            # Working in Singapore
            if dfworkingInfo['Working in Singapore'].item().lower() == "no":
                pass
            else:
                driver.find_element(
                    By.CSS_SELECTOR, 'p-radiobutton[name="workingInSingapore"]'
                ).click()
            sleep(1)
            print("Done : Working In Singapore")

            print("End Employement Information")
            # Next1
            Next1 = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next1)
            sleep(3)
            # Page 3/7 Guarantor 1
            print("Skip Guarantor")
            # skip guarantor
            
            # Next2
            Next2 = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next2)
            sleep(2)

            print("Starting Emergency Contact 1")
            # Page 4/7 Contact 1(Emergency)
            
            queryReferenceContact = f"SELECT * FROM `Reference Contact` WHERE NRIC={nric}"
            dfReferenceContact = pd.read_sql(queryReferenceContact, cnx)
            print(dfReferenceContact)
            
            # Add
            add3 = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div:nth-child(6) > app-contact-person > div > div > button').click()"
            add4 = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div:nth-child(6) > app-contact-person > div.p-field.mb-button.p-d-flex.p-jc-center.ng-star-inserted > button').click()"
            driver.execute_script(add3)
            sleep(1.3)
            driver.execute_script(add4)
            sleep(1.3)
            print("Done : Add 2 empty reference contact")
            # Name
            driver.find_element(
                By.CSS_SELECTOR, 'div.contact-person input[formcontrolname="firstName"]'
            ).send_keys(dfReferenceContact.iloc[0, 2])
            sleep(1)
            print("Done : First reference Name")
            relationship1 = dfReferenceContact.iloc[0, -1].lower()
            # Relationship
            driver.find_element(
                By.CSS_SELECTOR, 'div.contact-person p-dropdown[formcontrolname="relationship"]'
            ).click()
            sleep(2)
            if relationship1 == "spouse":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Spouse"]'
                ).click()
            elif relationship1 == "siblings":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Sibling"]'
                ).click()
            elif relationship1 == "parents":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Parents"]'
                ).click()
            elif relationship1 == "friends":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Friend"]'
                ).click()
            elif relationship1 == "relatives":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Other Relative"]'
                ).click()
            elif relationship1 == "children":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Children"]'
                ).click()
            sleep(1.2)
            print("Done : First reference Relationship")
            # Mobile Phone No
            driver.find_element(
                By.CSS_SELECTOR, 'div.contact-person input[formcontrolname="mobilePhone"]'
            ).send_keys(dfReferenceContact.iloc[0, 4][2::])
            sleep(1)
            print("Done : First reference Phone")
            print("End of Emergency Contact 1")
            # Contact 2(Emergency)
            # Name
            print("Start of Emergency Contact 2")
            driver.find_element(
                By.CSS_SELECTOR, 'div.contact-person:nth-child(2) input[formcontrolname="firstName"]'
            ).send_keys(dfReferenceContact.iloc[1, 2])
            sleep(1)
            print("Done : Second reference Name")
            relationship2 = dfReferenceContact.iloc[1, -1].lower()
            # Relationship
            driver.find_element(
                By.CSS_SELECTOR, 'div.contact-person:nth-child(2) p-dropdown[formcontrolname="relationship"]'
            ).click()
            sleep(2)
            if relationship2 == "spouse":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Spouse"]'
                ).click()
            elif relationship2 == "siblings":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Sibling"]'
                ).click()
            elif relationship2 == "parents":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Parents"]'
                ).click()
            elif relationship2 == "friends":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Friend"]'
                ).click()
            elif relationship2 == "relatives":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Other Relative"]'
                ).click()
            elif relationship2 == "children":
                driver.find_element(
                    By.CSS_SELECTOR, 'p-dropdownitem[ng-reflect-label="Children"]'
                ).click()
            sleep(1.2)
            print("Done : Second reference Relationship")
            # Mobile Phone No
            driver.find_element(
                By.CSS_SELECTOR, 'div.contact-person:nth-child(2) input[formcontrolname="mobilePhone"]'
            ).send_keys(dfReferenceContact.iloc[1, 4][2::])
            sleep(1)
            print("Done : Second reference Phone")
            print("End of Emergency Contact 2")
            # Next3
            Next3 = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next3)
            sleep(2)
            print("Start Product Information")
            # Page 5/7
            # Brand
            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown[formcontrolname="brand"]'
            ).click()
            sleep(1)
            brand = dfProductInfo['Brand'].item()
            brandSpan = wait.until(EC.visibility_of_element_located(
                (By.XPATH, f"//span[text()=\"{brand}\"]")))
            brandSpan.click()
            print("Done : Brand")
            sleep(2)

            model = dfProductInfo['Model'].item()
            # get model from model map
            #   secret vault
            cnx002 = pymysql.connect(
                host= dbip ,
                user= dbusername,
                password= dbpassword,
                database='crm_002_db',
            )

            queryModelMap = f"SELECT `Chailease` FROM `Model Map` WHERE Webform = '{model}'"
            modelMap = pd.read_sql(queryModelMap, cnx002)
            cnx002.close()
            if not modelMap["Chailease"].empty:
                model = modelMap['Chailease'].item()
            if model == None or model.lower() == 'null':
                print(f"No model found for webform model: {data['Model'].item()}")
                print("AUTOMATION STOPS NOW - INCORRECT/NON-EXISTING MODEL")
                raise Exception(f"No model found for webform model: {data['Model'].item()}")
            
            # Model
            driver.find_element(
                By.XPATH, "/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[2]/div/div[1]/div[2]/app-collateral-vehicle-motor/div/form/div/div[1]/div[3]/div[2]/div/p-autocomplete/span/input"
            ).send_keys(dfProductInfo['Model'].item())
            sleep(2)
            print("Done : Model")
            # Date of Manufacture
            driver.find_element(
                By.XPATH, "/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[2]/div/div[1]/div[2]/app-collateral-vehicle-motor/div/form/div/div[1]/div[4]/div[2]/p-calendar/span/input"
            ).send_keys("012023")
            sleep(1.2)
            print("Done : Date of Manufacture")
            # Purchase Price
            driver.find_element(
                By.XPATH, "/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[2]/div/div[1]/div[2]/app-collateral-vehicle-motor/div/form/div/div[1]/div[8]/div[2]/sigv-currency/div/sigv-input-number/span/input"
            ).send_keys(dfProductInfo['Price'])
            sleep(1.2)
            print("Done : Price")
            # Down Payment
            driver.find_element(
                By.XPATH, "/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[7]/app-collateral/div[1]/div/p-accordion/div/p-accordiontab/div/div[2]/div/div[1]/div[2]/app-collateral-vehicle-motor/div/form/div/div[2]/div/div[2]/sigv-currency/div/sigv-input-number/span/input"
            ).send_keys(dfProductInfo['Down Payment'])
            sleep(2.2)
            print("Done : Down Payment")
            # Next4
            Next4 = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next4)
            sleep(1.5)
            okbutton = "/html/body/p-dynamicdialog/div/div/div/sigv-error-dialog-accordion/div[3]/div/div/button"
            driver.find_element(By.XPATH, okbutton).click()
            sleep(1.5)
            driver.execute_script(Next4)
            sleep(2)
            print("End Product Information")
            # Page 6/7
            # Sales
            print("Start Sales and Terms")
            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown[formcontrolname="dealerSalesId"]'
            ).click()
            sleep(1)
            driver.find_element(
                By.CSS_SELECTOR, 'li[aria-label="MOTOSING SDN BHD"]'
            ).click()
            sleep(2)
            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown[formcontrolname="marketingOfficer"]'
            ).click()
            sleep(1)
            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown[formcontrolname="marketingOfficer"] .p-dropdown-item:first-child'
            ).click()
            sleep(1)
            print("Done : Sales")
            # Apply Terms
            driver.find_element(
                By.CSS_SELECTOR, 'p-dropdown[formcontrolname="tenureMonth"]'
            ).click()
            tenure = dfProductInfo['Tenure'].item()[:2]
            sleep(1.3)
            tenure_list = {
                "84" : 'p-dropdown [ng-reflect-label="84"]',
                "72" : 'p-dropdown [ng-reflect-label="72"]',
                "60" : 'p-dropdown [ng-reflect-label="60"]',
                "48" : 'p-dropdown [ng-reflect-label="48"]',
                "36" : 'p-dropdown [ng-reflect-label="36"]',
                "24" : 'p-dropdown [ng-reflect-label="24"]',
                "12" : 'p-dropdown [ng-reflect-label="12"]'
            }

            if tenure in tenure_list:
                driver.find_element(
                    By.CSS_SELECTOR, tenure_list[tenure]
                ).click()
            else:
                print("Invalid Tenure")
            sleep(1.2)
            print("Done : Tenure")
            # Next5
            Next5 = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-d-flex.p-jc-center.button > div:nth-child(2) > a').click()"
            driver.execute_script(Next5)
            sleep(3)
            print("End Sales and Terms")
            print("Start Upload and Download Files")
            # Download Application Form
            driver.find_element(
                By.CLASS_NAME, 'btn-tertiary'
            ).click()
            # sleep for download files
            sleep(5)
            # APPLICATION & CONSENT FORM(Individual)_20231017_094318123
            pattern =  r'APPLICATION & CONSENT FORM\(Individual\)_(\d+)_(\d+)\.pdf'
            directory = os.path.join(os.path.expandvars('%USERPROFILE%'),'Downloads')
            files = os.listdir(directory)
            for file in files:
                if re.match(pattern, file):
                    os.remove(os.path.join(directory,file))
                    print("Removed Application Form")
                    
            # Upload Income Documents
            target_directory = os.path.join(os.getcwd(), 'resources', 'LoanApplicantFolder')
            fullPath = os.path.join(target_directory, f'{nric}.zip')
            # fullPath = f'{nric}.zip'
            pdfFile = ""
            with zipfile.ZipFile(fullPath, 'r') as zip_ref:
                print("Unzipping :",zip_ref.filename)
                for file_name in zip_ref.namelist():
                    if file_name.endswith('.pdf'):
                        pdfFile = zip_ref.extract(file_name, target_directory)
                        print("Extracted :",pdfFile)
            #delete zip file
            try:
                os.remove(fullPath)
                print("Deleted ZIP file:", fullPath)
            except FileNotFoundError:
                print("ZIP file not found:", fullPath)

            driver.find_element(
                By.XPATH, "/html/body/app-root/div/app-extranet-layout/div/div/div/app-process/div[2]/div/div[9]/app-attachment/div/div/div/p-accordion/div/p-accordiontab[4]/div/div[2]/div/sigv-file-center/div/label/input"
            ).send_keys(pdfFile)
            sleep(2)

            # Confirm
            driver.find_element(
                By.XPATH, "/html/body/div[2]/div/div[3]/div/button[2]"
            ).click()
            sleep(2)
            print("Confirmed")
            
            # Agree Terms to Chailease
            tick_box = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > div > div > app-process > div.p-grid.ng-star-inserted > div > div.p-field.p-field-checkbox.mb-5.mt-7.ng-star-inserted > p-checkbox > div > div.p-checkbox-box').click()"
            driver.execute_script(tick_box)
            sleep(2)
            print("Ticked")
            
            # Submit Button
            submit = "document.querySelector('body > app-root > div.layout-wrapper > app-extranet-layout > div > div > div > app-process > div.page-action-container.p-d-flex.mb-20.currency.currency-rwd.ng-star-inserted > div > div > div:nth-child(1) > a').click()"
            print("Completed")
            driver.execute_script(submit)
            print("Sleep 20 seconds to load the submit success")
            sleep(20)
            
            # remove extracted pdfFile
            os.remove(pdfFile)
            os.remove(fullPath)
            print("Removed :", pdfFile)
            # input("STOP - Enter to continue")
    except Exception as e:
        filename = f"{nric}_Chailease_Automation.png"
        driver.save_screenshot(filename)
        errorlog(f'Error in Automation : {e}',traceback.format_exc(), filename)
        print(e, file=sys.stderr)
        raise Exception(e)

except Exception as e:
    try:
        os.remove(f'{nric}.zip')
    except:
        pass
    raise Exception(e)
    
finally:
    try:
        os.remove(f'{nric}.zip')
    except:
        pass
    kill_processes(os.path.basename(__file__))
