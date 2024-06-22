from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time
import random
from connector import collection

# List of user agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/54.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/15.15063",
]

# Mapping of Ukrainian months to their respective numbers
MONTH_MAPPING = {
    "січня": "01",
    "лютого": "02",
    "березня": "03",
    "квітня": "04",
    "травня": "05",
    "червня": "06",
    "липня": "07",
    "серпня": "08",
    "вересня": "09",
    "жовтня": "10",
    "листопада": "11",
    "грудня": "12",
}

def store_data(collection, data):
    if data:
        collection.insert_one(data)
    else:
        print("No data to store!")


def create_driver():
    options = Options()
    user_agent = random.choice(USER_AGENTS)
    options.set_preference("general.useragent.override", user_agent)
    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()), options=options
    )
    return driver


def transform_date(raw_date):
    # Remove "створено " and split the date string into components
    parts = raw_date.replace("створено ", "").split()
    if len(parts) == 2:
        day, month = parts
        month_number = MONTH_MAPPING.get(month)
        if month_number:
            return f"{day.zfill(2)}.{month_number}"
    return raw_date


def scrape_main_page(main_page_url, limit=10, retries=3):
    driver = create_driver()
    results = []

    try:
        driver.set_page_load_timeout(15)
        driver.get(main_page_url)
        time.sleep(
            random.uniform(5, 15)
        )  # Wait for the page to fully load with longer delay

        listings = driver.find_elements(By.XPATH, "//article[@class='realty-preview']")[
            :limit
        ]
        main_window = driver.current_window_handle

        for index, listing in enumerate(listings):
            for attempt in range(retries):
                try:
                    # Extract initial data
                    title = listing.find_element(
                        By.XPATH, ".//h3[@class='realty-preview-title']/button"
                    ).text
                    location = " ".join(
                        [
                            elem.text
                            for elem in listing.find_elements(
                                By.XPATH,
                                ".//div[@class='realty-preview-sub-title-wrapper']/a",
                            )
                        ]
                    )
                    price = listing.find_element(
                        By.XPATH,
                        ".//div[contains(@class, 'realty-preview-price--main')]",
                    ).text
                    size_elements = listing.find_elements(
                        By.XPATH,
                        ".//div[contains(@class, 'realty-preview-properties-item')]//span[@class='realty-preview-info']",
                    )
                    size = " ".join(
                        [elem.text for elem in size_elements if "м²" in elem.text]
                    )
                    raw_date = listing.find_elements(
                        By.XPATH,
                        ".//span[contains(@class, 'realty-preview-dates__value')]",
                    )[1].text
                    date = transform_date(raw_date)

                    # Extract the description
                    try:
                        description = listing.find_element(
                            By.XPATH,
                            ".//div[@class='realty-preview-description closed']//p",
                        ).text
                    except:
                        description = None
                        print("Description not found")

                    # Scroll the element into view and click the button to navigate to the detail page
                    detail_button = listing.find_element(
                        By.XPATH, ".//button[contains(@class, 'realty-link-button')]"
                    )
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", detail_button
                    )
                    ActionChains(driver).move_to_element(detail_button).click(
                        detail_button
                    ).perform()
                    time.sleep(
                        random.uniform(5, 15)
                    )  # Wait for the new page to load with longer delay

                    # Switch to new tab
                    driver.switch_to.window(driver.window_handles[-1])

                    # Capture the URL after navigation
                    url = driver.current_url

                    # Debugging: Print to understand the structure
                    print(f"Title: {title}")
                    print(f"Location: {location}")
                    print(f"Price: {price}")
                    print(f"Size: {size}")
                    print(f"Date: {date}")
                    print(f"URL: {url}")
                    print(f"Description: {description}")

                    results.append(
                        {
                            "title": title,
                            "location": location,
                            "price": price,
                            "size": size,
                            "date": date,
                            "description": description,
                            "url": url,
                        }
                    )

                    # Close the new tab and switch back to main window
                    driver.close()
                    driver.switch_to.window(main_window)
                    time.sleep(
                        random.uniform(5, 15)
                    )  # Wait for the main page to load with longer delay

                    break  # Exit the retry loop if successful

                except Exception as e:
                    print(
                        f"Error extracting data from listing {index + 1}, attempt {attempt + 1}: {e}"
                    )
                    time.sleep(
                        random.uniform(5, 15)
                    )  # Wait before retrying with longer delay

        driver.quit()
        return results

    except Exception as e:
        print(f"Error occurred while scraping main page: {e}")
        driver.quit()
        return []


def main():
    main_page_url = "https://flatfy.ua/uk/%D0%BF%D1%80%D0%BE%D0%B4%D0%B0%D0%B6-%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B8%D1%80-%D1%85%D0%B0%D1%80%D0%BA%D1%96%D0%B2"
    listings_data = scrape_main_page(main_page_url, limit=10)

    for data in listings_data:
        store_data(collection, data)

    print(f"Total scraped listings: {len(listings_data)}")


if __name__ == "__main__":
    main()
