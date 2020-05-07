from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from tqdm import tqdm
import argparse

from scraping_utils import element_exists, initialize_driver
from google_play_utils import scroll
from google_drive_utils import upload_df_to_gd, authenticate_google_drive

parser = argparse.ArgumentParser()
parser.add_argument("--from_scratch", type=bool, nargs='?', const=True, default=False,
                    help="Get list of apps from scratch (I.e. dont download them)")
parser.add_argument("--windows", type=bool, nargs='?', const=True, default=False,
                    help="Is this script running on windows?")
parser.add_argument("--chrome", type=bool, nargs='?', const=True, default=False,
                    help="Run on chrome?")
args = parser.parse_args()

def get_app_links_from_app_front(driver):
    WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.XPATH, "//div[@data-loadingmessage == 'Loading...']")))

    scroll(driver, 5)

    all_links_in_page = [x.get_attribute("href") for x in driver.find_elements_by_tag_name("a") if
                         x.get_attribute("href") is not None]

    category_links = list(set([x for x in all_links_in_page if "/store/apps/category/" in x]))
    unique_app_page_urls = list(set([x for x in all_links_in_page if "/store/apps/details?" in x]))
    cluster_page_urls = list(set([x for x in all_links_in_page if "/store/apps/collection/cluster?" in x]))

    return category_links, unique_app_page_urls, cluster_page_urls

def get_app_links(driver):
    ##### Get category Links
    url = "https://play.google.com/store/apps"

    driver.get(url)

    category_links, unique_app_page_urls, cluster_page_urls = get_app_links_from_app_front(driver)

    pbar = tqdm(category_links)
    for category_link in pbar:
        pbar.set_description(f"Category: {category_link}")
        driver.get(category_link)

        category_links_extended_new, unique_app_page_urls_new, cluster_page_urls_new = get_app_links_from_app_front(driver)

        unique_app_page_urls.extend(unique_app_page_urls_new)
        cluster_page_urls.extend(cluster_page_urls_new)

    cluster_page_urls = list(set(cluster_page_urls))

    pbar = tqdm(cluster_page_urls)
    for cluster_page_url in pbar:
        pbar.set_description(f"Cluster: {cluster_page_url}")
        driver.get(cluster_page_url)

        category_links_extended_new, unique_app_page_urls_new, cluster_page_urls_new = get_app_links_from_app_front(driver)

        unique_app_page_urls.extend(unique_app_page_urls_new)

    unique_app_page_urls = list(set(unique_app_page_urls))

    upload_df_to_gd("app_urls.csv", pd.DataFrame({"URL": unique_app_page_urls}), "1M8Mjk_vIVFtnFflcr60y7jD8UadMc5uk")
    upload_df_to_gd("category_urls.csv", pd.DataFrame({"URL": category_links}), "1M8Mjk_vIVFtnFflcr60y7jD8UadMc5uk")
    upload_df_to_gd("cluster_urls.csv", pd.DataFrame({"URL": cluster_page_urls}), "1M8Mjk_vIVFtnFflcr60y7jD8UadMc5uk")

    return unique_app_page_urls

def upload_app_data_from_url(unique_app_page_url, counter, driver):

    driver.get(unique_app_page_url)

    app_data = {x.find_element_by_xpath("./div").text: x.find_element_by_xpath("./span").text for x in
             driver.find_elements_by_xpath(
                 '//*[contains(text(), "Additional Information")]/../../div[2]/div[1]/div') if
             element_exists(x, "./span")}

    app_name = driver.find_element_by_xpath('//*[@itemprop="name"]').text
    app_company = driver.find_element_by_xpath(
     '//*[@itemprop="name"]/../following-sibling::div/div[1]/div/span[1]').text
    app_category = driver.find_element_by_xpath(
     '//*[@itemprop="name"]/../following-sibling::div/div[1]/div/span[2]').text
    app_price = driver.find_element_by_xpath(
     '//*[@itemprop="name"]/../../../div[2]/div/div[2]/div/c-wiz/c-wiz/div/span/button').get_attribute(
     "aria-label")
    app_description = driver.find_element_by_xpath('//*[@itemprop="description"]/span').text

    developer_url = driver.find_element_by_xpath('//a[text()="Visit website"]').get_attribute("href") if element_exists(driver, '//a[text()="Visit website"]') else None

    try:
        if element_exists(driver, '//*[contains(text(), "Reviews")]/../../c-wiz[1]/div[1]/div[1]'):
            average_rating = driver.find_element_by_xpath(
             '//*[contains(text(), "Reviews")]/../../c-wiz[1]/div[1]/div[1]').text
            number_of_reviews = driver.find_element_by_xpath(
             '//*[contains(text(), "Reviews")]/../../c-wiz[1]/div[1]/span[1]').text
            rating_distributions = [float(x.get_attribute("style").split("width: ")[1].split("%")[0]) for x in
                                 driver.find_elements_by_xpath(
                                     '//*[contains(text(), "Reviews")]/../../c-wiz[1]/div[2]/div/span[2]')]
        else:
            average_rating = driver.find_element_by_xpath(
             '//*[@itemprop="name"]/../following-sibling::div/div[2]/c-wiz[1]/div[1]/div[1]').get_attribute(
             "aria-label")
            number_of_reviews = driver.find_element_by_xpath(
             '//*[@itemprop="name"]/../following-sibling::div/div[2]/c-wiz[1]/span/span[1]').text
            rating_distributions = None
    except NoSuchElementException as err:
        print(f"Scraping reviews failed on {unique_app_page_url} with error message: \n {err}")
        average_rating = None
        number_of_reviews = None
        rating_distributions = None

    if len(driver.find_elements_by_xpath('//a[@aria-label="Check out more content from Similar"]')) > 0:
        similar_app_cluster_url = driver.find_element_by_xpath(
         '//a[@aria-label="Check out more content from Similar"]').get_attribute("href")
    else:
        similar_app_cluster_url = None

    if len(driver.find_elements_by_xpath('//a[@aria-label="Check out more content from Similar"]/../../../div[2]//a')) > 0:
        similar_app_urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath(
         '//a[@aria-label="Check out more content from Similar"]/../../../div[2]//a')]
    else:
        similar_app_urls = None

    app_data.update({
     "App URL": unique_app_page_url,
     "App name": app_name,
     "App company name": app_company,
     "App category name": app_category,
     "App price": app_price,
     "App description": app_description,
     "App average rating": average_rating,
     "App number of reviews": number_of_reviews,
     "App rating distribution": rating_distributions,
     "Developer URL": developer_url,
     "Similar apps cluster URL": similar_app_cluster_url,
     "Similar app URLs": similar_app_urls,
    })

    app_data = pd.DataFrame([app_data])

    # Make sure name only contains alphanumeric (There was a problem with pipes in file names)
    file_name = "".join(filter(str.isalnum, app_name)) + f"{counter}_appdata.csv"

    upload_df_to_gd(file_name, app_data, "1qUYsYjND3hOAmBFS2XDgxhimHCvbTpvb")

def upload_app_and_review_data(unique_app_page_urls, driver):

    for i, url in enumerate(unique_app_page_urls):
        print(url)
        upload_app_data_from_url(url, i, driver)

driver = initialize_driver(is_chrome=args.chrome, is_windows=args.windows)
app_urls = get_app_links(driver)

upload_app_and_review_data(app_urls, driver)
