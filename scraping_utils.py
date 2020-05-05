import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


# CHeck if element exists
def element_exists(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
        return True
    except Exception:
        return False

# Initializes the webdriver for the browser
def initialize_driver(is_chrome, is_windows):

    if is_chrome:
        opts = ChromeOptions()
        driver_name = "chromedriver"
    else:
        opts = FirefoxOptions()
        driver_name = "geckodriver"
    opts.add_argument("--headless")
    opts.add_argument("--width=1920")
    opts.add_argument("--height=1080")

    driver_suffix = ".exe" if is_windows else ""
    driver_path =  os.path.join(os.getcwd(), driver_name+driver_suffix)

    if is_chrome:
        driver = webdriver.Chrome(options=opts, executable_path=driver_path)
    else:
        driver = webdriver.Firefox(options=opts, executable_path=driver_path)
    return driver
