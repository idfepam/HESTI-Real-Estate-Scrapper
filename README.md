# HESTI Real Estate Scraper

## Overview 

This project involves scraping real estate listings from [Flatfy.ua](https://flatfy.ua). The script extracts key details such as title, location, price, size, date, description, and URL of the listing. The data is then stored in a MongoDB database. After scraping the data, we analyze it to calculate the average price per square meter for each location, categorize the listings, and generate visualizations.

## Setup Instructions

### Prerequisites

1. **Python**: Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. **MongoDB**: Install MongoDB on your system. Follow the installation guide from the [official MongoDB website](https://docs.mongodb.com/manual/installation/).

3. **WebDriver**: Ensure you have the appropriate WebDriver for Firefox (geckodriver) installed. This script uses `webdriver_manager` to handle WebDriver installation.

### Installing Required Packages

1. **Clone the repository**: Clone this repository to your local machine using:
   ```sh
   git clone https://github.com/idfepam/HESTI-Real-Estate-Scrapper.git
   cd <repository_directory>
   ```

2. **Create a virtual environment**:
   ```sh
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```sh
     source venv/bin/activate
     ```

4. **Install the required Python packages**:
   ```sh
   pip install -r requirements.txt
   ```

### Setting Up MongoDB

1. **Start MongoDB**: If MongoDB is installed, you can start it with:
   ```sh
   mongod
   ```

2. **Create the database and collection**:
   - Open another terminal and enter the MongoDB shell with:
     ```sh
     mongo
     ```
   - Create a new database and collection:
     ```sh
     use real_estate
     db.createCollection('land_listings')
     ```

3. **Restore Database from Dump**:
    If you want to use the provided dump files from the dump folder in this project, use the following command:
    ```sh
    mongorestore --host localhost --port 27017 --db real_estate --drop ./dump/real_estate
    ```
    This command will restore the real_estate database from the dump, dropping the existing database first if it exists.

## Website Structure

### Flatfy.ua

We are scraping data from the real estate section of [Flatfy.ua](https://flatfy.ua). Specifically, the script targets apartment listings in Kharkiv. 

### Key Elements on the Page

- **Article Element**: Each listing is encapsulated in an `<article>` element with the class `realty-preview`.
- **Title**: The title of the listing is found in an `<h3>` element with the class `realty-preview-title`.
- **Location**: Location information is contained in multiple `<a>` elements within a `div` with the class `realty-preview-sub-title-wrapper`.
- **Price**: The price is located in a `div` with the class `realty-preview-price--main`.
- **Size**: The size details are within `div` elements that have the class `realty-preview-properties-item`.
- **Date**: The date is located within a `span` element with the class `realty-preview-dates__value`.
- **Description**: The description can be found in a `div` with the class `realty-preview-description closed`.
- **URL**: The script navigates to the detailed page to capture the listing URL.

## Usage

### Task 1: Scraping

1. **Run the scraper**:
   ```sh
   python scrape_lands.py
   ```

   This will scrape the real estate listings from the specified URL and store them in the MongoDB database. Limit of scraped object is set to 10, but it can be changed to any number.

2. **Check the data in MongoDB**:
   - Open the MongoDB shell:
     ```sh
     mongo
     ```
   - Switch to the `real_estate` database:
     ```sh
     use real_estate
     ```
   - View the data in the `land_listings` collection:
     ```sh
     db.land_listings.find().pretty()
     ```

### Task 2: Data Analysis and Migration

1. **Run the analysis and migration script**:
   ```sh
   python analyze_lands.py
   ```

   This script will:
   - Connect to MongoDB and retrieve the data.
   - Calculate the average price per square meter for each location.
   - Categorize the listings into "Cheap", "Moderate", and "Expensive".
   - Update the MongoDB database with the new category field.
   - Generate and save a bar chart as `top_locations.png`.

### MongoDB Connector

The `connector.py` file is used to establish the MongoDB connection. Here is the content of the `connector.py` file:

```python
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["real_estate"]
collection = db["land_listings"] 
```

### Creating a MongoDB Database Dump

1. **Dump the MongoDB database**:
   ```sh
   mongodump --db real_estate --out /path_to_backup_directory
   ```

   This command will create a backup of the `real_estate` database in the specified directory.

## Script Explanation

### scrape_lands.py

The script performs the following tasks:

1. **Setup MongoDB connection**: Establishes a connection to the MongoDB database and collection.
2. **Create WebDriver**: Configures and creates a Firefox WebDriver with a randomized user agent to avoid detection and blocking.
3. **Scrape Main Page**: Navigates to the main page, extracts the necessary listing data, and stores it in MongoDB.

### analyze_lands.py

The script performs the following tasks:

1. **Setup MongoDB connection**: Establishes a connection to the MongoDB database and collection.
2. **Calculate price per square meter**: Computes the price per square meter for each listing.
3. **Categorize listings**: Adds a new field to categorize the listings into "Cheap", "Moderate", and "Expensive".
4. **Update MongoDB**: Updates the MongoDB collection with the new category field.
5. **Generate Bar Chart**: Creates and saves a bar chart showing the average price per square meter for the top 5 most expensive locations.

## Notes

- Ensure that you have a stable internet connection while running the script.
- Be mindful of the website's terms of service and do not overwhelm their servers with too many requests in a short period.
- Proxies and Captcha Solvers: I could have used proxies and captcha solvers to enhance the scraping process and avoid IP blocking. However, these solutions can be costly. Implementing them could be considered for future enhancements to handle more extensive scraping tasks.
- Date validation and further cleaning of the data should be handled in the data cleaning phase. This will ensure that all dates and other data points are correctly formatted and valid before being used for analysis or other purposes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
