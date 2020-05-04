from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# Scroll to the bottom of the page, and wait until
def scroll(driver, scroll_attempts_left):

    # First, scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # If the loading sign is detected, wait for it to dissappear, and then scroll again
    if len(driver.find_elements_by_xpath("//div[@data-loadingmessage='Loading...']")) > 0:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.XPATH, "//div[@data-loadingmessage='Loading...']"))
        )
        scroll(driver, scroll_attempts_left)

    # If the loading sign is not detected, it may be loading, in which case we scroll again, but with one less scroll attempt, effectively timing out after X many attempts
    else:
        if scroll_attempts_left > 0:
            scroll(driver, scroll_attempts_left - 1)
