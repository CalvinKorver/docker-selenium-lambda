import time

from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.common.by import By

mac_osx_testing = False
find_job_count = 2


def handler(event=None, context=None):
    options = webdriver.ChromeOptions()
    if mac_osx_testing:
        service = webdriver.ChromeService("chromedriver-mac-x64/chromedriver")
        options.binary_location = '/Applications/chrome-mac/Chromium.app/Contents/MacOS/Chromium'
    else:
        service = webdriver.ChromeService("/opt/chromedriver")
        options.binary_location = '/opt/chrome/chrome'
        options.add_argument('--headless')
        options.add_argument("--disable-dev-shm-usage")  # overcome limited resource problems
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=options, service=service)

    base_url = 'https://www.google.com/search?ibp=htl%3Bjobs&q=teacher'
    driver.get(base_url)
    job_elements = driver.find_elements(By.CLASS_NAME,
                                        "gws-plugins-horizon-jobs__li-ed")  # class name cannot have spaces fyi
    count = 0
    job_results = []
    for job in job_elements:
        if count > find_job_count:
            break

        job_description, job_info = [], []
        job_company, job_location, job_title, job_url = "", "", "", ""

        time.sleep(1)
        job.click()

        job_company = extract_text_by(By.XPATH, driver,
                                      '//*[@id="gws-plugins-horizon-jobs__job_details_page"]/div/div[1]/div/div[2]/div[2]/div[1]')
        job_location = extract_text_by(By.XPATH, driver,
                                       '//*[@id="gws-plugins-horizon-jobs__job_details_page"]/div/div[1]/div/div[2]/div[2]/div[2]')
        job_title = extract_text_by(By.XPATH, driver,
                                    '//*[@id="gws-plugins-horizon-jobs__job_details_page"]/div/div[1]/div/div[1]/h2')

        job_info_elements = driver.find_elements(By.CSS_SELECTOR,
                                                 '#gws-plugins-horizon-jobs__job_details_page > div > div.ocResc.KKh3md > div.I2Cbhb')
        for element in job_info_elements:
            if len(element.text) > 0:
                job_info.append(element.text)

        job_descriptions_elements = driver.find_elements(By.CLASS_NAME, "IiQJ2c")
        for element in job_descriptions_elements:
            if len(element.text) > 0:
                job_description.append(element.text)

        link_element = driver.find_elements(By.XPATH,
                                            '/html/body/div[2]/div/div[2]/div[1]/div/div/div[3]/div[2]/div/div[1]/div/div/g-scrolling-carousel/div[1]/div/div/span/a')
        for element in link_element:
            job_url = element.get_attribute('href')

        job_results.append(
            {"job_company": job_company, "job_title": job_title, "job_location": job_location, "job_info": job_info,
             "job_description": job_description, "job_url": job_url})
        count += 1

    driver.quit()

    return job_results


def extract_text_by(method, driver, path):
    elements = driver.find_elements(method, path)
    for element in elements:
        if len(element.text) > 0:
            return element.text
    return ""

# For testing
# def main():
#     print(handler(None, None))
#
# if __name__ == "__main__":
#     main()
