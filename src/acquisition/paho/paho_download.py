# IMPORTANT: This code is extremely unstable.
# Slight changes to the PAHO website may render this script partially or entirely useless.

import os

# Start up a browser
from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options

headerheight = 0


def wait_for(browser, css_selector, delay=10):
    try:
        WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
        WebDriverWait(browser, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
        print("Success Loading %s" % (css_selector))
    except TimeoutException:
        print("Loading %s took too much time!" % (css_selector))


def find_and_click(browser, element):
    element.location_once_scrolled_into_view
    browser.switch_to.default_content()
    browser.execute_script("window.scrollBy(0,-%d)" % headerheight)
    browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))
    browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))
    element.click()


def get_paho_data(offset=0, dir="downloads"):
    opts = Options()
    opts.set_headless()
    assert opts.headless  # Operating in headless mode

    fp = FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", os.path.abspath(dir))
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

    browser = Firefox(options=opts, firefox_profile=fp)
    browser.get("https://www.paho.org/data/index.php/en/mnu-topics/indicadores-dengue-en/dengue-nacional-en/252-dengue-pais-ano-en.html?showall=&start=1")
    tab1 = browser.window_handles[0]
    browser.execute_script("""window.open("","_blank");""")
    tab2 = browser.window_handles[1]
    browser.switch_to.window(tab1)

    curr_offset = offset

    wait_for(browser, "div.rt-top-inner", delay=30)
    header = browser.find_element_by_css_selector("div.rt-top-inner")
    global headerheight
    headerheight = header.rect["height"]

    # The actual content of the data of this webpage is within 2 iframes, so we need to navigate into them first
    browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))
    browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))

    # Locate the button that allows to download the table
    downloadoption = browser.find_elements_by_css_selector("div.tabToolbarButton.tab-widget.download")[0]
    find_and_click(browser, downloadoption)

    wait_for(browser, "div[data-tb-test-id='DownloadImage-Button']")

    # Locate the button that prepares the table for download as an image
    imagebutton = browser.find_elements_by_css_selector("div[data-tb-test-id='DownloadImage-Button']")[0]
    find_and_click(browser, imagebutton)

    wait_for(browser, ".tabDownloadFileButton[data-test-id='DownloadLink']")

    # Locate the button that downloads the table as an image
    downloadbutton = browser.find_elements_by_css_selector(".tabDownloadFileButton[data-test-id='DownloadLink']")[0]

    # Extract session ID
    href = downloadbutton.get_attribute("href")
    startidx = href.index("sessions/") + len("sessions/")
    endidx = href.index("/", startidx)
    sessionid = href[startidx:endidx]

    dataurl = (
        "https://phip.paho.org/vizql/w/Casosdedengue_tben/v/ByLastAvailableEpiWeek/viewData/sessions/%s/views/18076444178507886853_9530488980060483892?maxrows=200&viz=%%7B%%22worksheet%%22:%%22W%%20By%%20Last%%20Available%%20EpiWeek%%22,%%22dashboard%%22:%%22By%%20Last%%20Available%%20Epi%%20Week%%22%%7D"
        % sessionid
    )

    wait_for(browser, "div[data-tb-test-id='CancelBtn-Button']")

    # Cancel image download
    cancelbutton = browser.find_elements_by_css_selector("div[data-tb-test-id='CancelBtn-Button']")[0]
    find_and_click(browser, cancelbutton)

    wait_for(browser, "div[id='tableau_base_widget_FilterPanel_0']")

    # Default is to show data for current year, we want to get all years
    # Clicks drop-down menu to open options
    yearselector = browser.find_elements_by_css_selector("div[id='tableau_base_widget_FilterPanel_0']")[0]
    find_and_click(browser, yearselector)

    wait_for(browser, "div.facetOverflow")

    # Find option for all years and click it
    y = None
    for i in browser.find_elements_by_css_selector("div.facetOverflow"):
        if i.text == "(All)":
            y = i
    find_and_click(browser, y)

    for i in range(offset):
        gp = browser.find_element_by_css_selector("div.wcGlassPane")
        # print gp.is_enabled()
        # print gp.is_selected()
        # print gp.is_displayed()
        try:
            WebDriverWait(browser, 10).until(EC.staleness_of(gp))
            print("Loaded next week % d" % (53 - offset))
        except TimeoutException:
            print("Loading next week %d took too much time!" % (53 - offset))
        gp = browser.find_element_by_css_selector("div.wcGlassPane")
        # print gp.is_enabled()
        # print gp.is_selected()
        # print gp.is_displayed()
        x = browser.find_elements_by_css_selector("div.dijitReset.dijitSliderButtonContainer.dijitSliderButtonContainerH.tableauArrowDec")[0]
        find_and_click(browser, x)

    # Cycle through all weeks, downloading each week as a separate .csv
    # Theoretically, need to cycle 53 times, but in practice only 54 works, unsure why
    for i in range(54 - offset):
        # If something goes wrong for whatever reason, try from the beginning
        try:
            print("Loading week %d" % (53 - i))
            # (Re-)load URL
            browser.switch_to.window(tab2)
            browser.get(dataurl)

            wait_for(browser, "li[id='tab-view-full-data']")
            # Load data in better format ("Full Data")
            full_data_tab = browser.find_elements_by_css_selector("li[id='tab-view-full-data']")[0]
            full_data_tab.click()

            wait_for(browser, "a.csvLink")  # Sometimes this fails but the button is successfully clicked anyway, not sure why
            # Actually download the data as a .csv (Will be downloaded to Firefox's default download destination)
            data_links = browser.find_elements_by_css_selector("a.csvLink")
            data_link = None
            for i in data_links:
                if i.get_property("href") != "":
                    data_link = i
                    break
            data_link.click()

            # Locate button that decreases the current week by 1
            browser.switch_to.window(tab1)
            wait_for(browser, "div.dijitReset.dijitSliderButtonContainer.dijitSliderButtonContainerH.tableauArrowDec")

            x = browser.find_elements_by_css_selector("div.dijitReset.dijitSliderButtonContainer.dijitSliderButtonContainerH.tableauArrowDec")[0]
            find_and_click(browser, x)
            curr_offset += 1
        except Exception as e:
            print("Got exception %s\nTrying again from week %d" % (e, 53 - offset))
            browser.quit()
            get_paho_data(offset=curr_offset)
    browser.quit()


if __name__ == "__main__":
    get_paho_data(dir="downloads/")
