from selenium import webdriver
from bs4 import BeautifulSoup
import time
import csv

# List of city URLs to scrape
city_urls = [
    "https://www.cardekho.com/used-cars+in+new-delhi",
    "https://www.cardekho.com/used-cars+in+gurgaon",
    "https://www.cardekho.com/used-cars+in+mumbai",
    "https://www.cardekho.com/used-cars+in+chandigarh",
    "https://www.cardekho.com/used-cars+in+bangalore",
    "https://www.cardekho.com/used-cars+in+hyderabad",
    "https://www.cardekho.com/used-cars+in+pune",
    "https://www.cardekho.com/used-cars+in+ahmedabad",
    "https://www.cardekho.com/used-cars+in+jaipur",
    "https://www.cardekho.com/used-cars+in+chennai"
]

# Initialize the web driver
driver = webdriver.Chrome()

# File to save the data
output_file = "Cars_Details.csv"

# List to store all car details
all_car_details = []


# Function to convert price into lakhs
def convert_price_to_lakhs(price_text):
    if "Lakh" in price_text:
        return round(float(price_text.replace("₹", "").replace("Lakh", "").strip()), 2)
    elif "Crore" in price_text:
        return round(float(price_text.replace("₹", "").replace("Crore", "").strip()) * 100, 2)
    else:
        return "N/A"


# Clean price
def clean_price(price):
    try:
        return round(price, 2)
    except:
        return "N/A"


# Clean seats
def clean_seats(seats):
    try:
        return int(seats.replace(' Seats', '').strip())
    except:
        return "N/A"


# Clean kms
def clean_kms(kms_text):
    try:
        return int(kms_text.replace(' Kms', '').replace(',', '').strip())
    except:
        return "N/A"


# Clean engine
def clean_engine(engine_text):
    try:
        return int(engine_text.replace(' cc', '').replace(',', '').strip())
    except:
        return "N/A"


# Clean power
def clean_power(power_text):
    try:
        return float(power_text.replace(' bhp', '').replace(',', '').strip())
    except:
        return "N/A"


# Clean mileage
def clean_mileage(mileage_text):
    try:
        return float(mileage_text.replace(' kmpl', '').replace(',', '').strip())
    except:
        return "N/A"


# Clean year
def clean_year(year_text):
    try:
        return int(year_text.strip())
    except:
        return "N/A"


# Function to extract specific car details
def extract_car_details(car_url, driver):
    if not car_url:
        return {}

    try:
        driver.get(car_url)
        time.sleep(2)  # Give the page time to load

        # Scroll to load more content if necessary
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Parse the content
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        car_details = {}

        # Extract the overview section
        elements = soup.find_all("div", class_="gsc_row posR")
        for element in elements:
            title = element.find_all('div', class_="gsc_col-xs-12 gsc_col-md-7 gsc_col-lg-8 outerLeft vdpPage")
            for tags in title:
                tag = tags.find('div', class_="outer-card-container posR")
                if tag:
                    details = tag.find_all('li', class_="gsc_col-xs-12 gsc_col-md-6")
                    for detail in details:
                        label = detail.find('div', class_="label-text")
                        if label:
                            label_text = label.find('div', class_="label")
                            value_text = label.find('span', class_="value-text")
                            if label_text and value_text:
                                label_str = label_text.text.strip()
                                value_str = value_text.text.strip()
                                car_details[label_str] = value_str

                tag = tags.find('div', class_="outer-card-container specsCard")
                if tag:
                    details = tag.find_all('li', class_="gsc_col-xs-12 gsc_col-md-6")
                    for detail in details:
                        label = detail.find('div', class_="label-text")
                        if label:
                            label_text = label.find('div', class_="label")
                            value_text = label.find('span', class_="value-text")
                            if label_text and value_text:
                                label_str = label_text.text.strip()
                                value_str = value_text.text.strip()
                                car_details[label_str] = value_str

        return car_details

    except Exception as e:
        print(f"Error extracting car details from {car_url}: {e}")
        return {}


# Loop through each city URL
for city_url in city_urls:
    driver.get(city_url)
    print(f"Scraping data from: {city_url}")

    # Store the initial number of car cards
    previous_car_count = 0
    scroll_attempts = 0

    # Loop to ensure the page loads new cars
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(4)

        # Parse the loaded content
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Extract car cards
        car_cards = soup.find_all("div", class_="gsc_col-xs-12 gsc_col-sm-6 gsc_col-md-4 cardColumn")

        # Check if new cars have been loaded
        current_car_count = len(car_cards)
        if current_car_count == previous_car_count:
            scroll_attempts += 1
            if scroll_attempts >= 3:  # Stop after 3 failed attempts to load new cars
                break
        else:
            scroll_attempts = 0
            previous_car_count = current_car_count

    # Loop through each card and extract details
    for car_data in car_cards:
        # Extract car name and URL
        title_div = car_data.find("div", class_="titlebox hover")
        car_url = None

        if title_div:
            car_link = title_div.find("a", href=True)
            full_title = car_link['title'].strip() if car_link else "N/A"
            car_url = car_link['href'].strip() if car_link else None

            # Add prefix only if the URL is not complete
            if car_url and not car_url.startswith("http"):
                car_url = f"https://www.cardekho.com{car_url}"

            # Extract car name (e.g., "Mahindra Thar")
            car_name = " ".join(full_title.split()[1:3]) if full_title != "N/A" else "N/A"
        else:
            car_name, full_title, car_url = "N/A", "N/A", None

        # Extract price and convert to lakhs
        price_div = car_data.find("div", class_="Price hover")
        raw_price = price_div.find("p").text.strip() if price_div else "N/A"
        car_price = convert_price_to_lakhs(raw_price)

        # Extract location and city
        location_div = car_data.find("div", class_="distanceText")
        raw_location = location_div.text.strip() if location_div else "N/A"
        car_city = raw_location.split(",")[-1].strip() if "," in raw_location else raw_location.strip()

        # Extract car details from the specific page
        car_details = extract_car_details(car_url, driver) if car_url else {}

        # Clean and retain only required columns
        required_columns = [
            "Registration Year", "Insurance", "Fuel Type", "Seats", 
            "Kms Driven", "RTO", "Ownership", "Engine", 
            "Transmission", "Power", "Drive Type", "Mileage", "Year of Manufacture"
        ]

        # Clean specific details
        car_data_row = [
            full_title, car_name, car_url, car_price, raw_location, car_city
        ]

        for col in required_columns:
            value = car_details.get(col, "N/A")
            if col == "Seats":
                car_data_row.append(clean_seats(value))
            elif col == "Kms Driven":
                car_data_row.append(clean_kms(value))
            elif col == "Engine":
                car_data_row.append(clean_engine(value))
            elif col == "Power":
                car_data_row.append(clean_power(value))
            elif col == "Mileage":
                car_data_row.append(clean_mileage(value))
            elif col == "Year of Manufacture":
                car_data_row.append(clean_year(value))
            else:
                car_data_row.append(value)

        # Append this car's details to the master list
        all_car_details.append(car_data_row)

    print(f"Completed scraping {len(all_car_details)} cars from {city_url}")

# Save the data to a CSV file
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Full Title", "Car Name", "URL", "Price (in Lakhs)", "Location", "City",
                     "Registration Year", "Insurance", "Fuel Type", "Seats", 
                     "Kms Driven", "RTO", "Ownership", "Engine", "Transmission", 
                     "Power", "Drive Type", "Mileage", "Year of Manufacture"])
    writer.writerows(all_car_details)

print(f"Data has been saved to {output_file}")
