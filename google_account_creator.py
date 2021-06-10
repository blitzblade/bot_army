from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from proxy_mob import create_driver
from time import sleep
import json

URL = "https://accounts.google.com/"
SMS_URL = "https://receive-smss.com/"

driver = create_driver()

driver.get(URL)

def get_data():
    return json.load(open("database.json"))

def set_data(data):
    json.dump(data, open("database.json","w"))

def add_account(account, data):
    data["accounts"].append(account)
    set_data(data)

def enter_detail_by_id(driver, id, data, wait=1):
    sleep(wait)
    _input = driver.find_element_by_id(id)
    _input.clear()
    _input.send_keys(data)

def enter_detail_by_name(driver, name, data, wait=1):
    sleep(wait)
    _input = driver.find_element_by_name(name)
    _input.clear()
    _input.send_keys(data)

create_account_link = driver.find_element_by_xpath("//button//span[contains(text(),'Create account')]")

create_account_link.click()
sleep(1)
driver.find_element_by_xpath("//span[contains(text(),'For myself')]").click()


## enter details

enter_detail_by_id(driver, "firstName", "Kwesi")
enter_detail_by_id(driver, "lastName", "Dadson")
enter_detail_by_id(driver, "username","kdadson")

enter_detail_by_name(driver,"Passwd","Everlasting")
enter_detail_by_name(driver,"ConfirmPasswd","Everlasting")


#check if email not available
available = driver.find_elements_by_xpath("//li[contains(text(),'Available:')]")
if len(available) > 0: #suggestion 
    suggested_email = driver.find_element_by_xpath("//li[contains(text(),'Available:')]/following-sibling::li").text
    print("suggested: ", suggested_email)
    enter_detail_by_id(driver, "username", suggested_email)

driver.find_element_by_xpath("//*[contains(text(),'Next')]").click()

def handle_security_error(driver):
    #check for error
    sleep(10)
    try:
        driver.find_element_by_id("advancedButton").click()
        sleep(1)
        driver.find_element_by_id("exceptionDialogButton").click()
        sleep(1)
    except Exception as ex:
        print("No security risk button seen...")

driver.execute_script(f'''window.open("{SMS_URL}","_blank");''')

print("about to handle error")

# sms_driver = create_driver("https://receive-smss.com/")
#get phone number from another tab
# driver.execute_script('''window.open("https://receive-smss.com/","_blank");''')

# actions = ActionChains(driver)
# actions.key_down(Keys.COMMAND).send_keys('t').perform()
windows = driver.window_handles
print("windows")
print(windows)
driver.switch_to.window(windows[1])
handle_security_error(driver)

driver.get(SMS_URL) #refresh
container = driver.find_element_by_class_name("number-boxes")

number_links = container.find_elements_by_tag_name('a')
account = {

}
data = get_data()
all_numbers = [account["number"] for account in data["accounts"]]
for number_link in number_links:
    href = number_link.get_attribute("href")
    number = f'+{href.split("/sms/")[1].replace("/","")}'
    if number in all_numbers:
        next
    else:
        account["number"] = number
        actions = ActionChains(driver)
        driver.execute_script("arguments[0].click()", number_link)
        break




driver.switch_to.window(windows[0])
enter_detail_by_id(driver, "phoneNumberId",account["number"])
driver.find_element_by_xpath("//*[contains(text(),'Next')]").click()

driver.switch_to.window(windows[1])
sleep(5)
driver.get(SMS_URL+account["number"].replace("+",""))
#pick number and insert it in 
# try this url: https://mytempsms.com/receive-sms-online/uk-phone-number-7988235573.html
#and that: https://america.materialtools.com/sms_content/9735069282
sleep(500)
driver.quit()
