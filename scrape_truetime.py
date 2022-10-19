import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import bs4
import re

# This module scrapes HTML pages from the Pittsburgh Port Authority TrueTime tool. The resulting dicts are then used by
# the CreateDB class to create the routes and stops tables.

# Primary function called by outside modules is get_stop_list().

# This function checks the HTML page for a particular bus route, and determines whether the route includes INBOUND
# buses, OUTBOUND buses, both, or neither. The result is two booleans values: outbound and inbound.
def check_available_directions(route_num: str) -> (bool, bool):
    url = f'https://truetime.portauthority.org/bustime/wireless/html/selectdirection.jsp?route=Port%20Authority%20Bus:{route_num}'
    page = requests.get(url)
    # Specify lxml parser to avoid different defaults on different machines
    soup = bs4.BeautifulSoup(page.text, features='lxml')
    soup = soup.text
    inbound = False
    outbound = False
    if 'OUTBOUND' in soup:
        outbound = True
    if 'INBOUND' in soup:
        inbound = True

    return outbound, inbound


# This function takes in a url and HTML tag, and then scrapes the url for the given tag. It returns a list of strings,
# which contains every string found inside the given tag at the given url.
def scrape_html_tag(url, tag):
    page = requests.get(url)
    # Specify lxml parser to avoid different default parsers on different machines
    soup_object = bs4.BeautifulSoup(page.text, features='lxml')
    tagged_elements = soup_object.find_all(tag)

    result = []
    for element in tagged_elements:
        result.append(element.string)
    return result


# This function takes in a url, which should be the page on the TrueTime website which lists all the stops available for
# a given route and direction. The function also takes in information about direction, route ID, route name. Using the
# given URL, the function scrapes the ID and name of each bus stop, and packages it together with the other parameters
# as a dict with the following structure for each key/value pair: {StopID: [StopName, Direction, RouteID, RouteName]}
def zip_stop_id_and_name(url: str, direction: str, r_num: str, r_name: str) -> dict:
    page = requests.get(url)
    # Specify lxml parser to avoid different default parsers on different machines
    soup_object = bs4.BeautifulSoup(page.text, features='lxml')

    # Find all links on the page.
    page_links = soup_object.find_all('a', attrs={'href': re.compile(r'^eta.jsp')})

    stop_info = {}
    for link in page_links:
        link_address = link.get('href')
        # Strip off the end of the link using regex.
        end_of_link = re.search(r'id=Port\+Authority\+Bus%3A[0-9]+', link_address).group()
        # Get the stop_id from the end_of_link str using regex. Exploit the fact that the str we want always starts with
        # A.
        stop_id = re.search(r'A[0-9]+', end_of_link).group()
        # Strip off the A.
        stop_id = stop_id[1:]

        # Validate result, which should be str matching a numeric value (all official stop_ids are numbers).
        if not stop_id.isnumeric():
            raise Exception("Bad Stop Id!")

        # Process stop_id and add to stop_info.
        stop_id = int(stop_id)
        stop_name_from_link = link.text
        stop_name = stop_name_from_link.strip()
        stop_info[stop_id] = [stop_name, direction, r_num, r_name]

    return stop_info


# This function take a URL and an HTML class name as input, and outputs a list of strings containing all the information
# found under the given url and class tag. Unlike bs4, Selenium works for content served dynamically by JavaScript.
def scrape_dynamic_tag(url, class_name):
    # This is boilerplate code that initializes a Chrome web driver for use by the Selenium library.
    options = Options()
    # Stop browser windows from actually popping up.
    options.add_argument('--headless')
    # Install a browser for use by Selenium.
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    # Scrape the list of available routes from the TrueTime homepage using Selenium.
    result = []
    # Search for elements in dynamically-served HTML matching certain tags.
    driver_result = driver.find_elements(By.CLASS_NAME, class_name)
    for r in driver_result:
        result.append(r.text)
    driver.quit()

    return result


# This is the main function for this module. It takes no arguments, and outputs a list of dicts. There is a dict for
# each line/direction combination (e.g. 71A OUTBOUND). Each key in each dict represents a unique bus stop/bus route
# combination. Most bus stops have multiple lines that stop there, so between the different dicts there are identical
# keys.

# Input: None
# Output: get_stop_list() returns a list of dicts. There are 0-2 dicts per bus route, depending on whether INBOUND and
#         OUTBOUND versions both exist for that route. Each dict has the following structure:
#         {StopIDNumber: [StopName, Direction, RouteID, RouteName]
def get_stop_list():
    url = 'https://truetime.portauthority.org/bustime/wireless/html/home.jsp'
    # Scrape the route names
    routes = scrape_dynamic_tag(url, 'larger')

    list_of_dicts = []

    for route in routes:
        print('Now scraping information from this route:', route)
        r_elements = route.split('-')  # Split the route to get the route num, and route name
        r_name = r_elements[1].strip()
        r_num = r_elements[0].strip()  # The 0-index item in the list is the number

        # Check whether inbound and outbound are available for each route
        outbound, inbound = check_available_directions(r_num)

        # INBOUND and OUTBOUND are separate HTML pages that must be scraped separately.
        if outbound:
            url = f'https://truetime.portauthority.org/bustime/wireless/html/selectstop.jsp?route=Port+Authority+Bus%3A{r_num}&direction=Port+Authority+Bus%3AOUTBOUND'
            out_stop_names_and_ids: dict = zip_stop_id_and_name(url, 'OUTBOUND', r_num, r_name)
            list_of_dicts.append(out_stop_names_and_ids)

        if inbound:
            url = f'https://truetime.portauthority.org/bustime/wireless/html/selectstop.jsp?route=Port+Authority+Bus%3A{r_num}&direction=Port+Authority+Bus%3AINBOUND'
            in_stop_names_and_ids: dict = zip_stop_id_and_name(url, 'INBOUND', r_num, r_name)
            list_of_dicts.append(in_stop_names_and_ids)

    return list_of_dicts


# For debugging purposes. This function uses bs4 to scrape static webpages for the purpose of learning what tags are
# available to scrape.
def exploratory_scrape():
    url = f'https://truetime.portauthority.org/bustime/wireless/html/selectstop.jsp?route=Port+Authority+Bus%3A1&direction=Port+Authority+Bus%3AOUTBOUND'
    page = requests.get(url)
    # Specify lxml parser to avoid different defaults on different machines
    soup = bs4.BeautifulSoup(page.text, features='lxml')
    links = soup.find_all('a')  # Gets route and ETA, but not vehicle number
    # for link in links:
    #     print(link.string)
    print(soup.prettify())


# For debugging purposes. This function tests the output from get_stop_list() to see how many bus lines are associated
# with each bus stop.
def test_results():
    cnt = 0
    list_of_dicts = get_stop_list()
    list_of_ids = []
    for d in list_of_dicts:
        for key in d.keys():
            list_of_ids.append(key)
    print("Length before", len(list_of_ids))
    test_dict = {}
    for i in list_of_ids:
        if i in test_dict:
            test_dict[i] += 1
        if i not in test_dict:
            test_dict[i] = 1

    for key, value in test_dict.items():
        if value != 1:
            print("Outer Key =", key)
            for d in list_of_dicts:
                for inner_key, value in d.items():
                    if inner_key == key:
                        print(inner_key, value)
