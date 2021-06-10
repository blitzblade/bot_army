from browsermobproxy import Server
from time import sleep 
from selenium import webdriver
import sys

from multiprocessing import Pool, cpu_count, freeze_support
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from time import sleep
import random
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

global server
server = None

def print_err(err):
    print(str(err) + " on line " + str(sys.exc_info()[2].tb_lineno))


def search_string_to_query(search_string):
    search = search_string.split(' ')
    query = '+'.join(search)
    return query

def destroy_driver(driver):
    try:
        driver.quit()
        if server != None:
            server.stop()
    except Exception as ex:
        print_err(ex)

def create_driver(url=None):

    sleep(1)
    server = Server("/Users/kwesi_dadson/kwesi_bin/browsermob-proxy-2.1.4/bin/browsermob-proxy")
    server.start()
    proxy = server.create_proxy()
    sleep(1)

    profile  = webdriver.FirefoxProfile()
    profile.set_proxy(proxy.selenium_proxy())
    profile.accept_untrusted_certs = True
    driver = webdriver.Firefox(firefox_profile=profile)
    if url:
        driver.get(url)
    return driver


def search_and_click(ua,sleep_time,search_string,driver,sleep_after):

    query = search_string_to_query(search_string)
    driver.get('https://www.youtube.com/results?search_query=%s'%query)
    
    try:
        # section_list = driver.find_element_by_class_name('section-list')
        section_list = driver.find_element_by_xpath('//a[contains(@href,"watch")]')
        section_list.click()
        print("Section list found...")
        sleep(random.randint(10, 20))
        # wait = WebDriverWait(driver, 15)    
        # wait.until(EC.element_to_be_clickable((By.XPATH,"//button[@aria-label='More actions']"))).click()
        # link.click()
        # link = section_list.find_element_by_class_name('yt-uix-tile-link')
        # link = driver.find_element_by_xpath("//div[@id='menu']/ytd-menu-renderer/yt-icon-button[@id='button']")
        link = driver.find_element_by_xpath("//button[@aria-label='More actions']")
        
        # wait = WebDriverWait(driver, 15)    
        # wait.until(EC.element_to_be_clickable((By.XPATH,"//button[@aria-label='More actions']"))).click()
        # link.click()
        print("Link element: ", link)
        driver.execute_script("arguments[0].setAttribute('id','blitz_button');", link)
        sleep(2)
        print("attribute set...")
        driver.execute_script("document.getElementById('blitz_button').click();")
        # actions = ActionChains(driver)
        # actions.move_to_element(link).perform()
        print("More actions button found...")
        
        # sleep(500)
        # link.click()
        
        print("Tile link found")
        report_link = driver.find_element_by_xpath("//*[text()='Report']")
        sleep(1)
        report_link.click()
        print("Report clicked...")
        sleep(500)

        report_radio_button = driver.find_element_by_xpath("//*[text()='Harassment or bullying']")
        report_radio_button.click()

        #select option from drop down
        # write a short paragraph
        
        print("Successfully reported...")
        sleep(sleep_time)
    
        destroy_driver(driver)
        print("Browser quit gracefully")
        
        if sleep_after is not None:
            sleep(sleep_after)
    
    except Exception as ex:
        print_err(ex)
        destroy_driver(driver)
        driver = create_driver()
        search_and_click(ua,sleep_time,search_string,driver,sleep_after)
        
def parse_line(line):
    delim_loc = line.find('=')
    return line[delim_loc+1:].strip()

def read_config(config_string):
    try:
        search_string = parse_line(config_string[0])
        min_watch = int(parse_line(config_string[1]))
        max_watch = int(parse_line(config_string[2]))
        sleep_after = int(parse_line(config_string[3]))
        views = int(parse_line(config_string[4]))
        multicore = parse_line(config_string[5])
        if multicore != 'True':
            multicore = False
        if sleep_after == 'None':
            sleep_after = None
        return search_string,sleep_after, min_watch, max_watch, views, multicore
    except:
        write_defaults()
        return 'Bad File', 'RIP', 'Bad File', 'RIP', 'Bad File', 'RIP'
    
def write_defaults():
    with open('config.txt', 'w') as config:
        config.write('search_string = Your Search Here\n')
        config.write('min_watch = 10\n')
        config.write('max_watch = 45\n')
        config.write('wait_after = 15\n')
        config.write('views = 100\n')
        config.write('multicore = False')

# write_defaults()

if __name__ == "__main__":
    freeze_support()
    with open('config.txt', 'r') as config:
        config_values = config.readlines()
    
    search_string, sleep_after, min_watch ,max_watch, views, multicore = read_config(config_values)
    if min_watch == 'Bad File':
        i = 'rip'
    elif multicore:
        threads = int(cpu_count()*0.75)
        pool = Pool(threads)
        ua = UserAgent()
        for i in range(views):
            sleep_time = random.randint(min_watch,max_watch)
            driver = create_driver()
            pool.apply_async(search_and_click, args=[ua,sleep_time,search_string,driver,sleep_after])
        pool.close()
        pool.join()
    else:
        ua = UserAgent()
        for i in range(views):
            sleep_time = random.randint(min_watch,max_watch)
            driver = create_driver()
            search_and_click(ua,sleep_time,search_string,driver,sleep_after)
