############################## Changeable Variables ##############################
DEBUG = True
HEADLESS = True
PATH = "chromedriver.exe" # chrome driver's path
MAX_NUM_TRIALS = 30
SLEEP_BTWN_TRIALS = 0.2
###################################################################################
groupTxts = []
importSuccess = False
print("Importing libraries...")
from msvcrt import getch
try:
    # Other Libraries
    from time import sleep
    import getpass 
    import warnings
    import ctypes
    import datetime

    # Selenium Components   
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import Select
    
    importSuccess = True
except ImportError:
    print("It seems that some libraries has not beeen installed yet.")
    print("Did you installed all libraries in the 'requirements.txt' ?")

def isLoaded():
    pageState = myBrowser.execute_script('return document.readyState;')
    return pageState == 'complete'

def waitUntilLoaded():
    while not isLoaded():
        print("Waiting page to load")
        sleep(SLEEP_BTWN_TRIALS)
    return

def login():
    uNameBox = myBrowser.find_element_by_xpath('//*[@id="username"]')
    passWdBox = myBrowser.find_element_by_xpath('//*[@id="password"]')
    btnSignIn = myBrowser.find_element_by_xpath('//*[@id="loginbtn"]')

    uNameBox.send_keys(username)
    passWdBox.send_keys(passwd)
    passWdBox.send_keys(Keys.ENTER)
    waitUntilLoaded()

    numTrials = 0
    while numTrials<MAX_NUM_TRIALS:
        try:
            dashboard = myBrowser.find_element_by_xpath("/html/body/div[2]/div[2]/div/div[2]/section/aside/section[1]/div/div/ul/li/p/a")
            print("Password and username are correct!")
            myBrowser.refresh()
            break
        except Exception as ex:
            if DEBUG:
                print(ex)
            numTrials += 1
            sleep(SLEEP_BTWN_TRIALS)

    if numTrials<MAX_NUM_TRIALS:
        print("Continueing to app...")
        return True
    else:
        print("End of max trials: Probably, password or username are/is wrong. Please reenter.")
        return False

def scrape(groupTxt):
    ttbr = "" # text to be returned
    # https://stackoverflow.com/questions/7867537/how-to-select-a-drop-down-menu-value-with-selenium-using-python
    # https://www.tutorialspoint.com/how-to-select-the-text-of-a-span-on-click-in-selenium

    btnApply = myBrowser.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/section/div/div[2]/div[3]/button[3]")
    # btnClear = myBrowser.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/section/div/div[2]/div[3]/button[2]")
    cboxSelect = myBrowser.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/section/div/div[2]/div[2]/div/fieldset/div[1]/select")
    select = Select(cboxSelect)
    select.select_by_visible_text('Groups')
    sleep(SLEEP_BTWN_TRIALS)
    textBoxTypeOrSelect = myBrowser.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/section/div/div[2]/div[2]/div/fieldset/div[1]/div[2]/div[1]/input")
    
    textBoxTypeOrSelect.send_keys(groupTxt)
    sleep(SLEEP_BTWN_TRIALS)
    textBoxTypeOrSelect.send_keys(Keys.ENTER)
    
    btnApply.click()
    sleep(SLEEP_BTWN_TRIALS)
    table = myBrowser.find_element_by_tag_name("tbody")
    for tr in table.find_elements_by_tag_name("tr"):
        text = tr.text.split()
        text = " ".join(text[:-2])
        if text:
            # print(text)
            ttbr += text + '\n'
    
    return ttbr
    
def getGroupTxts():
    global groupTxts
    # btnApply = myBrowser.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/section/div/div[2]/div[3]/button[3]")
    cboxSelect = myBrowser.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/section/div/div[2]/div[2]/div/fieldset/div[1]/select")
    select = Select(cboxSelect)
    select.select_by_visible_text('Groups')
    sleep(SLEEP_BTWN_TRIALS)
    cboxBoxTypeOrSelect = myBrowser.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/section/div/div[2]/div[2]/div/fieldset/div[1]/div[2]")
    cboxBoxTypeOrSelect.click()
    # textBoxTypeOrSelect = myBrowser.find_element_by_xpath("/html/body/div[1]/div[2]/div/div[1]/section/div/div[2]/div[2]/div/fieldset/div[1]/div[2]/div[1]/input")
    btnDownArrow = myBrowser.find_element_by_css_selector("span[class='form-autocomplete-downarrow position-absolute p-1']")
    btnDownArrow.click()
    sleep(SLEEP_BTWN_TRIALS)
    groupUl = myBrowser.find_element_by_class_name("form-autocomplete-suggestions")
    groups = groupUl.find_elements_by_tag_name("li")
    groupTxts = [group.text for group in groups]
    groupTxts = groupTxts[8:]
    if DEBUG:
        print(groupTxts)
    
if importSuccess:
    try:
        print("Initalizing browser(s)...")
        myOptions = Options()
        if HEADLESS:
            myOptions.add_argument("--headless") # get rid of window
        myOptions.add_argument("--start-maximized")
        myOptions.add_argument("--no-sandbox")
        myOptions.add_argument("--log-level=3") # ovoid boring log messages
        
        warnings.filterwarnings("ignore", category=DeprecationWarning) # get rid of deprecation warnings printed on console
        myBrowser = webdriver.Chrome(PATH, chrome_options=myOptions)

        print("Loading ODTUCLASS...")
        myBrowser.get("https://odtuclass2021f.metu.edu.tr/login/index.php")
        waitUntilLoaded()

        while True:
            print("#"*70)
            username = input("--> Enter Username: ")
            passwd = getpass.getpass("--> Enter Password: ")
            print("#"*70)
            waitUntilLoaded()
            if login():
                break
        
        myBrowser.get("https://odtuclass2021f.metu.edu.tr/user/index.php?id=4813")
        waitUntilLoaded()
        getGroupTxts()
        while True:
            try:
                number = int(input("Enter the experiment number to scrape (enter '-1' to scrape all available data)\n--> "))
                if number >= -1:
                    break
                else:
                    print("Number must be greater than or equal to -1.")
            except:
                print("Number must be an integer")
        if number > -1:
            groupTxts = [item for item in groupTxts if f"Exp-{number}" in item]
        customDT = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        print(f"{customDT}: {len(groupTxts)} group found. Scraping started!")
        filename = "Scraped" + customDT + ".txt"
        with open(filename, "a", encoding="utf-8") as fil:
            fil.write(f"{'EE361 Experiment Groups'.center(75, '=')}\nRetrieved @ {customDT} from ODTUCLASS\nDisclaimer: Developer is not responsible for any wrong data. Use this document by acknowledging this.\n{'='*75}\n\n")
        for i, groupTxt in enumerate(groupTxts):
            myBrowser.refresh()
            waitUntilLoaded()
            print(f"--> {str(i+1).zfill(3).rjust(4)}. Scraping: {groupTxt}")
            res = scrape(groupTxt)
            print(res.rjust(5))
            with open(filename, "a", encoding="utf-8") as fil:
                fil.write(f"--> {groupTxt}\n{res}{'-'*30}\n")
        customDT = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
        print(f"{customDT}: Scraping completed succesfully.")
        with open(filename, "a", encoding="utf-8") as fil:
            fil.write("\n\n")
            fil.write("#"*75 + '\n') 
            fil.write(f"{customDT}: Scraping completed succesfully.")

    except (Exception, OSError, RuntimeError, ImportError, ValueError, IOError, IndexError, OverflowError, TypeError, ArithmeticError) as ex:
        print("An error occured:")
        print(ex)

print("Press any key to exit.")
getch()
try:
    print("Closing browser, please wait...")
    myBrowser.quit()
except:
    print("Browser never has been launched")