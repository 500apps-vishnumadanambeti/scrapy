import requests
import xmltodict
import random
import string
import time
import json
import certifi
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

options = Options()
options.add_argument("--start-maximized")  # Maximize the browser window

driver = webdriver.Chrome(options=options)

prox = [
    "http://hbsatya:125487dcfgawpong_country-us_session-igd4mvub_lifetime-1m@geo.iproyal.com:42324",
    "http://hbsatya:125487dcfgawpong_country-us_session-xzprsmr9_lifetime-15s@geo.iproyal.com:42324",
    "http://hbsatya:125487dcfgawpong_country-us_session-x7k340t8_lifetime-15s@geo.iproyal.com:42324"
]

def parse_sitemap(url):
    response = requests.request("GET", url, timeout=30)
    content = response.content
    sitemap_dict = xmltodict.parse(content)
    urls = []
    for child in sitemap_dict.get('urlset', {}).get('url', []):
        urls.append(child.get('loc'))
    return urls

def get_links(sitemap_url, blacklist_tokens=["expired", "search-result-pages.xml"]):
    urls = parse_sitemap(sitemap_url)
    return urls

sitemap_url = "https://www.99acres.com/sitemaps/afterhttps-main-urls.xml"
links = get_links(sitemap_url)
links = list(set(links))
print('Final count:', len(links))
ignore_links = ['https://www.99acres.com/', 'https://www.99acres.com/register.html']
links = [link for link in links if link not in ignore_links]
print(len(links))

property_data = []

for link in links:
    proxy = {
        'http': random.choice(prox),
        'https': random.choice(prox)
    }

    try:
        response = requests.get(link, proxies=proxy, verify=certifi.where())
        response.raise_for_status()
        response = response.text

        soup = BeautifulSoup(response, 'html.parser')

        anchor_tags = soup.select("div.featuredProjectsCard__contentText.pageComponent a")
        if anchor_tags:
            data = []
            for element in anchor_tags:
                url = element.get('href')
                if url:
                    json_data = {"URL": url}

                    driver.maximize_window()

                    # Open a URL
                    driver.get(url)

                    try:
                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[3]/div/div[2]/button')))
                        element.click()
                    except TimeoutException:
                        print("Timeout occurred while waiting for the element to be clickable.")

                    try:
                        element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="Banner__photonWrap pageComponent"]')))
                        element.click()
                    except TimeoutException:
                        print("Timeout occurred while waiting for the element to be clickable.")

                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'PhotonFilmStrip')))
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')

                    parent_element = soup.find('ul', id='PhotonFilmStrip')

                    if parent_element:
                        image_elements = parent_element.find_all('img')
                        image_hrefs = []
                        for image in image_elements:
                            href = image.get('src')
                            if href:
                                image_hrefs.append(href)
                        print(image_hrefs)
                        json_data["Images"] = image_hrefs or ["Image not found"]
                    else:
                        print("Parent element not found.")

                    property_name = soup.find('h1', class_='ProjectInfo__imgBox1.title_bold')
                    json_data["property_name"] = property_name.get_text(strip=True) if property_name else "Property name not found"

                    cost = soup.find('span', class_='list_header_semiBold.configurationCards__configurationCardsHeading')
                    json_data["cost of the property"] = cost.get_text(strip=True) if cost else "Cost not found"

                    status = soup.find('div', class_='ProjectInfo__imgBox1.title_bold.ConstructionStatus__phaseStatus')
                    json_data["status"] = status.get_text(strip=True) if status else "Status not found"

                    rating = soup.find('div', class_='ratingByFeature__ratingDesktopWrap.ratingByFeature__deskWrap.pageComponent')
                    json_data["rating"] = rating.get_text(strip=True) if rating else "Ratings not found"

                    About = soup.find('div', class_='AboutBuilder__desc.body_med.pageComponent.ReadMoreLess__prewrap')
                    json_data["about"] = About.get_text(strip=True) if About else "About not found"

                    BHK_Apartment = soup.find('div', class_='configurationCards__cardContainer')
                    json_data["BHK_Apartment"] = BHK_Apartment.get_text(strip=True) if BHK_Apartment else "BHK_Apartment not found"

                    Facilities = soup.find('div', class_='UniquesFacilities__facilitiesCardWrap')
                    json_data["facilities"] = Facilities.get_text(strip=True) if Facilities else "Facilities not found"

                    Specifications = soup.find('div', class_='specificationCards__cardContainer')
                    json_data["specifications"] = Specifications.get_text(strip=True) if Specifications else "Specifications not found"

                    Questions = soup.find('div', class_='Faq__fnqWrap')
                    json_data["Questions"] = Questions.get_text(strip=True) if Questions else "Frequently Asked Questions not found"

                    property_data.append(json_data)
                    data.append(json_data)

                    time.sleep(3)  # Add a wait of 3 seconds between requests

            print(data)  # Print the data for each link

    except (requests.RequestException, TimeoutError, ValueError) as e:
        print(f"Error occurred for link {link}: {str(e)}")
        continue

# Open file and write JSON string
with open("output1.json", "w") as file:
    json.dump(property_data, file, indent=4, sort_keys=True)

# Quit the driver to close the browser
driver.quit()
