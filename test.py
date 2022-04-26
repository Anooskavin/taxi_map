# import geocoder
# import socket
# import requests
# # ip = socket.gethostbyname(socket.gethostname())
# # g = geocoder.freegeoip(ip)
# # g.json


# from requests import get

# ip = get('https://api.ipify.org').text

# def get_ip():
#     response = requests.get('https://api64.ipify.org?format=json').json()
#     return response["ip"]


# def get_location():
#     ip_address = ip
#     response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
#     location_data = {
#         "ip": ip_address,
#         "city": response.get("city"),
#         "region": response.get("region"),
#         "country": response.get("country_name"),
#         "latitude": response.get("latitude"),
#         "longitude": response.get("longitude")
#     }
#     return location_data


# print(get_location())

# import geocoder
# g = geocoder.ip('me')
# print(g.latlng[0])

import requests
import urllib.parse

bang_add = 'Bangalore'
url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(bang_add) +'?format=json'

response = requests.get(url).json()
print("Banglore")
print(response[0]["lat"])
print(response[0]["lon"])

chen_add = 'Chennai '
url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(chen_add) +'?format=json'

response = requests.get(url).json()
print("Chennai")
print(response[0]["lat"])
print(response[0]["lon"])

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time

def getLocation():
    options = Options()
    options.add_argument("--use--fake-ui-for-media-stream")
    driver = webdriver.Chrome(executable_path = './chromedriver.exe',options=options) #Edit path of chromedriver accordingly
    timeout = 20
    driver.get("https://mycurrentlocation.net/")
    wait = WebDriverWait(driver, timeout)
    time.sleep(3)
    longitude = driver.find_elements_by_xpath('//*[@id="longitude"]')  # Replace with any XPath
    longitude = [x.text for x in longitude]
    longitude = str(longitude[0])
    latitude = driver.find_elements_by_xpath('//*[@id="latitude"]')
    latitude = [x.text for x in latitude]
    latitude = str(latitude[0])
    driver.quit()
    return (latitude, longitude)
print(getLocation())


