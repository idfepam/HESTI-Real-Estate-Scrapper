import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.firefox import GeckoDriverManager

# Initialize the Selenium WebDriver
def init_driver():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    return driver

# Function to click an element using XPath
def click_element(driver, xpath):
    try:
        elements = driver.find_elements(By.XPATH, xpath)
        if elements:
            elements[0].click()
            time.sleep(3)
    except Exception as e:
        print(f"Element with xpath {xpath} not found or clickable. Exception: {e}")

# Function to scrape zones from the first website
def scrape_zones_airway_heights(driver):
    zones = []
    zone_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Zone') and not(starts-with(text(), 'Zone'))]")

    for link in zone_links:
        zone_name = link.text.strip().split(' ', 1)[1]  # Extracting text without the leading chapter number
        if "Zone Classifications" in zone_name:  # Skip the first unwanted element
            continue

        zone_url = link.get_attribute('href')
        
        try:
            # Open the zone URL in a new tab
            driver.execute_script("window.open(arguments[0], '_blank');", zone_url)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3)

            try:
                header_elements = driver.find_elements(By.XPATH, "//*[@class='Cite']")
                content_elements = driver.find_elements(By.XPATH, "//*[@class='P1' or @class='P2' or @class='P3']")
                
                headers = [header.text for header in header_elements]
                contents = [content.text for content in content_elements]

                zone_description = ' '.join(headers + contents)
            except NoSuchElementException:
                zone_description = "Description not found"
            
            zones.append({
                'name': zone_name,
                'description': zone_description,
                'link': zone_url
            })

            # Close the tab and switch back to the main window
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(3)
        except Exception as e:
            print(f"Failed to scrape description from {zone_url}: {e}")
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(3)

    return zones

# Function to check if the name is valid based on the given conditions
def is_valid_name(name):
    sentences = name.split('.')
    if len(sentences) > 1:
        return False
    if name.strip().lower().startswith("district"):
        return False
    return True

# Function to clean the name by removing leading hyphen and unnecessary parts
def clean_name(name):
    name = name.split('-', 1)[-1].strip()
    if name.startswith("-"):
        name = name[1:].strip()
    return name

# Function to scrape zones from the second website (Albion)
def scrape_districts_albion(driver):
    districts = []
    # Click on the zoning link to navigate to the zoning page
    click_element(driver, "/html/body/div[3]/div[2]/ui-view/mcc-codes/div[2]/nav/div[2]/div[2]/mcc-codes-toc/mcc-product-toc/div/ul/li[14]/a")
    time.sleep(3)

    # Find all district links on the zoning page
    district_links = driver.find_elements(By.XPATH, "/html/body/div[3]/div[2]/ui-view/mcc-codes/div[2]/main/div[1]/mcc-codes-content/div/div[2]/div[2]/ul/li/mcc-codes-content-mini-toc-item/div/div/a")
    
    for link in district_links:
        raw_district_name = link.text.strip().split(' ', 2)[2]  # Extracting text without the leading chapter number
        district_name = clean_name(raw_district_name)
        if "district" in district_name.lower() and is_valid_name(district_name):
            district_url = link.get_attribute('href')

            try:
                # Open the district URL in a new tab
                driver.execute_script("window.open(arguments[0], '_blank');", district_url)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(3)

                try:
                    description_element = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/ui-view/mcc-codes/div[2]/main/div[1]/mcc-codes-content/div/div[2]/ul/li[2]')
                    district_description = description_element.text
                except NoSuchElementException:
                    district_description = "Description not found"

                districts.append({
                    'name': district_name,
                    'description': district_description,
                    'link': district_url
                })

                # Close the tab and switch back to the main window
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(3)
            except Exception as e:
                print(f"Failed to scrape description from {district_url}: {e}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(3)

    return districts

# Function to scrape zones from the third website (Algona)
def scrape_districts_algona(driver):
    districts = []
    # Click on the zoning link to navigate to the zoning page
    click_element(driver, "/html/body/div[1]/div[4]/div/div/main/div/div/div/a[15]")
    time.sleep(3)

    # Find all district links on the zoning page
    district_links = driver.find_elements(By.XPATH, "/html/body/div[1]/div[4]/div/div/main/div/article/ul/li/a")
    
    for link in district_links:
        raw_district_name = link.find_element(By.XPATH, "./span[2]").text.strip()
        district_name = clean_name(raw_district_name)
        if "district" in district_name.lower() and is_valid_name(district_name):
            district_url = link.get_attribute('href')

            try:
                # Open the district URL in a new tab
                driver.execute_script("window.open(arguments[0], '_blank');", district_url)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(3)

                try:
                    description_elements = driver.find_elements(By.XPATH, "//*[@class='level6 chunking-small type-Section has-history']")
                    district_description = ' '.join([element.text for element in description_elements])
                except NoSuchElementException:
                    district_description = "Description not found"

                districts.append({
                    'name': district_name,
                    'description': district_description,
                    'link': district_url
                })

                # Close the tab and switch back to the main window
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(3)
            except Exception as e:
                print(f"Failed to scrape description from {district_url}: {e}")
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(3)

    return districts

# Main function to scrape all provided URLs
def main():
    urls_xpaths = [
        ("https://www.codepublishing.com/WA/AirwayHeights", "//*[@id='AirwayHeights17']", scrape_zones_airway_heights),
        ("https://library.municode.com/wa/albion/codes/code_of_ordinances", "/html/body/div[3]/div[2]/ui-view/mcc-codes/div[2]/nav/div[2]/div[2]/mcc-codes-toc/mcc-product-toc/div/ul/li[14]/a", scrape_districts_albion),
        ("https://algona.municipal.codes/", "/html/body/div[1]/div[4]/div/div/main/div/div/div/a[15]", scrape_districts_algona)
    ]

    all_zones = {}
    driver = init_driver()

    for url, xpath, scrape_function in urls_xpaths:
        try:
            print(f"Scraping {url}")
            driver.get(url)
            time.sleep(3)
            click_element(driver, xpath)
            zones = scrape_function(driver)
            all_zones[url] = zones
        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    # Save the results to a JSON file
    with open('zones.json', 'w') as f:
        json.dump(all_zones, f, indent=2)
    print("Scraping complete. Results saved to zones.json")
    driver.quit()

if __name__ == "__main__":
    main()
