"""
Created on Tue Mar 17 12:41:03 2020
@author: jingjingtang and rumackaaron
"""

import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def download_ecdc_data(download_dir = "downloads"):
    url = 'https://flunewseurope.org/WebForms/ViewReport.aspx?ReportName=dinfl06&SDId=2325&SUrl=https%3a%2f%2fflunewseurope.org%2fPrimaryCareData%2fIndex%2fshare%2fdinfl06%3fts%3d20200317232612783%23dinfl06'
    opts = webdriver.firefox.options.Options()
    opts.set_headless()
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList",2)
    fp.set_preference("browser.download.manager.showWhenStarting",False)
    fp.set_preference("browser.download.dir",os.path.abspath(download_dir))
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")
    try:
        driver = webdriver.Firefox(options=opts,firefox_profile=fp)
        driver.get(url)
        for i in range(2, 54):
            # select country
            try:
                elt = WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.ID,'fluNewsReportViewer_ctl04_ctl03_ddValue')))
                Select(driver.find_element_by_tag_name('select')).select_by_value(str(i))
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                options = soup.select('#fluNewsReportViewer_ctl04_ctl05_ddValue')[0].find_all('option')
                ind = 1
                for j in range(len(options)):
                    if 'ILI' in str(options[j]):
                        pattern = re.compile(r'\d+')
                        ind = re.findall(pattern, str(options[j]))[0]
                        break
                if type(ind) == str:
                    # select clinical tyle
                    elt = WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.ID,'fluNewsReportViewer_ctl04_ctl05_ddValue')))
                    Select(driver.find_element_by_id('fluNewsReportViewer_ctl04_ctl05_ddValue')).select_by_value(ind)
                    elt = WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.ID,'btnSelectExportType')))
                    driver.find_element_by_id('btnSelectExportType').click()
                    elt = WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.ID,'btnExportToCsv')))
                    driver.find_element_by_id('btnExportToCsv').click()
                time.sleep(3)
            except:
                driver.get(url)
    except:
        print('WARNING: ECDC Scraper may not have downloaded all of the available data.')
    #cleanup
    os.system('''pkill "firefox" ''')
    os.system('''pkill "(firefox-bin)"''')
    os.system('''pkill "geckodriver*"''')
