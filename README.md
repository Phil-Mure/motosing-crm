# CRM Desktop Application

## Framework - Electron + ExpressJS + Python (selenium, scrapy, mechanicalsoup, playwright)

Desktop Application is adopt from a web application.

Desktop app works by starting a express server on the local, and redirecting the main window to the express app url.

## Getting started

**Make sure to install MYSQLserver**
Very important to make sure enviroment viarables consist MYSQL server at /bin and also the password should be 1234

(https://downloads.mysql.com/archives/installer/)

**Make sure you have Nodejs Python installed** 

All below commands are run at root directory `*/CRM_desktop> command`. All commands can be viewed at root level `package.json` under `scripts`.

1. After git clone, you will not have the `./resources/executables` folder as it is too huge to be pushed into the repo, so, compile the scripts into executables first by running

        pip install -r requirements.txt

        npm run compile

2. With the scripts compiled, you need to have the node modules to be installed as it will **not** be in the git repository

        npm install 

3. For developmet, to instantly open the application, do 

        npm run dev

    It will start an instance of the desktop application, and you can start testing!

    If you encounter the error of `Resources Locked while executing /path/to/file` when running the above command after closing an instance, just open task manager and end the application task.

4. After that, you can either start packaging first to see the application or you can start making distributable by going to the next step. For packaging first, run the following command

        npm run package

    This will produce a executable application in `./out/app_name-OS-ARCH`. 

## Scripts / Automation
Python scripts locate at `./Automation`, it is not configured with a repo or any submodules that has any relation to the other main repo **Automation**.

Any modification or updates on the scripts need to be done seperately in this **CRM_Desktop** repo as well as the **Automation**. 

When running scripts, it might download some zip files or pdf files to the root directory as it is the working directory when running the application.

#### SFTP

For retrieving zipfiles from server, it will use a sftp script that can be found in `Automation/utils/sftp.py`. The function to retrieve the zipfile is imported for each scripts.

It will take in nric and save the zipfile into `(working_directory)/nric.zip`. All the scripts will be getting the file based on current working directory which is `*/CRM_desktop`.

#### Note that when packaging and distributing, it will default to host machine's OS, meaning that if its host machine OS is windows, it will default to win32 and following the architecture such as x64

## Compiling python scripts
Compiling python scripts should occur before packaging through the use of `npm run compile`. Alternatively, compiling can automatically occur through **prepackage** hook that can be implemented in the **package.json** file in scripts.

### Process to compile scripts
This can be found in the **compile.py**, the process flow, is to find all the Automation scripts, and bundle/package them into one standalone executable that can be found in *executables* folder.

After compiling, it will proceed to package entire node js application and also copying the `executables` folder into the `/out/app_name/resources`. This will be used in the production desktop application to run the script.

To compile specific script, go to `compily.py` and look for the CLI that is commented

### Compiling Scrapy 

Scrapy works differently than other scripts, as it has tons of dependencies, so, it will break if you tried to build the __\_\_init\_\_.py__ to gather all dependencies to be build it as a standalone executable. 
But, thanks to [this](https://stackoverflow.com/questions/75308876/error-after-running-exe-file-originating-from-scrapy-project), it provides a thorough guide to solve this problem. 

Basically, you need to specify all the required depencies and hooks by Scrapy in the spec file, which is created when first executing `PyInstaller __init__.py`.

This spec file is basically a configuration to tell what the installer going to do. Currently, in `build/__spec__` is where all the spec file will be located, this is specified in the **compile.py**.

In **compile.py** there is already a custom code that will run separately to install scrapy project. If need to configure anything for extra modules, can refer to the spec file as well documentations as to how to append them.


[More information](https://stackoverflow.com/questions/49085970/no-such-file-or-directory-error-using-pyinstaller-and-scrapy)


## Packaging

When packaging the application, the configuration can be found at `forge.config.js` at `packagerConfig`. You will see that there are several **ignored** files and folders, this is to avoid packing unnessary files into the packaged version. For the **extra resource**, it is required to copy the entire executable folder into the packaged version to be able to execute the script by the desktop application. Additionally, during packaging all JS file will be **obfuscated** hence after packaging do remember to **git clone the source code again** OR go to your source control in your editor and discard all changes made so that the code go back to its original form.

## Auto-Update / Maintainence / Release

To release a new version of the desktop application, you need to package it **(update the version number in package.json)**, and then find the packaged folder, it will be in `out/app_name` and then add the `crmUpdater.exe` inside the folder, and then zip it by selecting all files in the folder, and right click, compress. Rename it to `Motosing.CRM-win32-x64`.

**`Note that the zip file should be containing all the files and not a directory and then all the files.`**

Go to `Github Release`, create a new release with a new tag of the `package version` which can be found in `package.json`. The title should be `package version` e.g. `1.0.5`. Drag and drop the zip file, and set it as latest release, publish the release. 

Its important to note that `npm run publish` will not work cause the crmUpdater.exe will not be packaged correctly.

## Error Logging

When there is an error in the application or scripts, it will be logged into the database. Refer to it for more details

### Errors that might trying to compile the script

    Requested Module was not found: No module named 'mysql.connector.plugins.caching_sha2_password'

    1117 WARNING: lib not found: libmysql.dll dependency of C:\Users\user\AppData\Roaming\Python\Python311\site-packages\_mysql_connector.cp311-win_amd64.pyd

    ImportError: No localization support for language 'eng'

The above 3 error code can be found if MySQL is not setup/installed correctly in your machine.

For this, please make sure that you have MySQL installed in your machine, as well adding the binaries or entire folder into your Environment PATH (if you are using windows).

Currently, it has manually added **libmysql.dll** binary file through CLI, there will be some dependencies that this binary file needs, please make sure to include them.

#### Playwright not installed correctly 
Go to [this page](https://playwright.dev/python/docs/library#pyinstaller) and follow the instructions to bundle the browser correctly along with playwright.

## Future Improvements

Changing the automation scripts to javascript, so that when bundling dont need to perform extra step and requiring extra dependencies.

Change scrapy to be using other framework, as it will hard to configure the dependencies if there are any extra modules or libraries.

Changing AEON and JCL to be not using a text file, instead use locator to check for the current page

## Task List

dealers role
- see employees review
- manage staffs account ✔
- default can only create 5 accounts ✔
- sign up ✔
- after 5 min inactivity, logout ✔
- loan accounts : setting finance accounts credentials for finance websites ✔
- when new dealer is created, duplicate databases ✔
    - crm_DBNAME_db
    - crm_DBNAME_staffs
    - crm_DBNAME_customer
- when creating new staff, prefix it with name@COMPANYNAME.com ✔
- change password ✔

staff role
- can only perform basic functions ✔
- cannot see settings ✔
- able to login back after close out application automatically unless logged out ✔
- when login, get the COMPANYNAME, and then go their db and attempt to login ✔

need to change the webform's database part ✔
need to change crm desktop app to be using dynamic database ✔
