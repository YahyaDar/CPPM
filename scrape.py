from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime

csv_f = open(f"scrape_output/data_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S:%f")}.csv", "x")
data_file_name = csv_f.name
csv_f.close()

# Set up Selenium WebDriver
option = Options()
option.headless = True
driver = webdriver.Chrome(options=option)

NUMBER_OF_PAGES = 1000
PAGE_NUMBER = 1

# Load the webpage(s)
for i in range(NUMBER_OF_PAGES):

    if PAGE_NUMBER == 1:
        page = 'https://www.pakwheels.com/used-cars/search/-/'

    elif PAGE_NUMBER > 1:
        page = 'https://www.pakwheels.com/used-cars/search/-/?page=' + str(PAGE_NUMBER)

    url = page
    driver.get(url)

    # Get page source and create BeautifulSoup object
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find the div with id="main-container"
    main_container = soup.find('div', id='main-container')

    if main_container:
        # Find all script tags inside the main container
        script_tags = main_container.find_all('script', type='application/ld+json')

        json_data_list = []

        # Extract JSON data from each script tag
        for script in script_tags:
            json_data = script.string
            try:
                data = json.loads(json_data)

                # Check if @type is WebPage or ItemList and skip those entries
                if '@type' in data and data['@type'] not in ['WebPage', 'ItemList']:
                    json_data_list.append(data)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")

        # Ensure at least one JSON object is found
        if json_data_list:
            # Convert JSON data to DataFrame using pandas
            df = pd.DataFrame(json_data_list)

            # Remove columns @context, @type, and image if they exist
            columns_to_drop = ['@context', '@type', 'image']
            df = df.drop(columns=columns_to_drop)

            # Extract brand name from the brand column
            df['brand'] = df['brand'].apply(lambda x: x['name'])

            # Extract location from description column
            df['location'] = df['description'].apply(
                lambda x: x[x.find("for sale in") + len("for sale in"):].strip() if "for sale in" in x else ""
            )

            # Extract car model from description column
            df['modelDate'] = df['modelDate'].astype(str)
            df['model'] = df.apply(lambda row: row['description'].replace(row['manufacturer'], '').replace(row['modelDate'], '').split('for sale')[0].strip(), axis=1)

            # Drop the original description column
            df.drop(columns=['description'], inplace=True)

            # Drop unwanted columns
            df.drop(columns=['manufacturer', 'name'], inplace=True)

            # Extract engine specification from the vehicleSpecification column
            df['vehicleEngine'] = df['vehicleEngine'].apply(lambda x: x['engineDisplacement'])

            # Extract price from the offers column
            df['offers'] = df['offers'].apply(lambda x: x['price'])

            # Rename offers column to price
            df.rename(columns={'offers': 'price'}, inplace=True)

            # Define CSV file path
            csv_file = open(data_file_name, 'a')

            # Save DataFrame to CSV
            df.to_csv(csv_file, mode='a', index=False, header=not bool(PAGE_NUMBER - 1))

            print(f'Page {PAGE_NUMBER} complete, Data saved to {csv_file.name}')
        else:
            print("No valid JSON-LD data found in the main container")
    else:
        print("Main container with id='main-container' not found")

    PAGE_NUMBER += 1

# Close Selenium WebDriver
driver.quit()
