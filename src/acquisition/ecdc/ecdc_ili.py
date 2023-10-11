"""
Created on Tue Mar 17 12:41:03 2020
@author: jingjingtang and rumackaaron
"""

import os
import re
import requests
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def download_ecdc_data(download_dir="downloads"):
    url = "https://flunewseurope.org/PrimaryCareData"
    resp = requests.get(url)
    soup = BeautifulSoup(resp.content, "lxml")
    mydivs = soup.findAll("div")
    for div in mydivs:
        dic = div.attrs
        if dic.get("class") == ["graph-container"] and dic.get("id") == "dinfl06":
            break
    # get new url of the ILI chunck
    url = div.contents[1].attrs["src"]
    opts = webdriver.firefox.options.Options()
    opts.set_headless()
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", os.path.abspath(download_dir))
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
    try:
        driver = webdriver.Firefox(options=opts, firefox_profile=fp)
        driver.get(url)
        for i in range(2, 54):
            # select country
            try:
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "fluNewsReportViewer_ctl04_ctl03_ddValue"))
                )
                Select(driver.find_element_by_tag_name("select")).select_by_value(str(i))
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                options = soup.select("#fluNewsReportViewer_ctl04_ctl05_ddValue")[0].find_all(
                    "option"
                )
                ind = 1
                for j in range(len(options)):
                    if "ILI" in str(options[j]):
                        pattern = re.compile(r"\d+")
                        ind = re.findall(pattern, str(options[j]))[0]
                        break
                if type(ind) == str:
                    # select clinical tyle
                    WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable(
                            (By.ID, "fluNewsReportViewer_ctl04_ctl05_ddValue")
                        )
                    )
                    Select(
                        driver.find_element_by_id("fluNewsReportViewer_ctl04_ctl05_ddValue")
                    ).select_by_value(ind)
                    WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.ID, "btnSelectExportType"))
                    )
                    driver.find_element_by_id("btnSelectExportType").click()
                    WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.ID, "btnExportToCsv"))
                    )
                    driver.find_element_by_id("btnExportToCsv").click()
                time.sleep(3)
            except:
                driver.get(url)
    except:
        print("WARNING: ECDC Scraper may not have downloaded all of the available data.")
    # cleanup
    os.system("""pkill "firefox" """)
    os.system('''pkill "(firefox-bin)"''')
    os.system('''pkill "geckodriver*"''')
