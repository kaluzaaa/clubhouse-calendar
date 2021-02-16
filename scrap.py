from bs4 import BeautifulSoup
import requests
import re
import datetime
import json
from dateutil import parser
from dateutil import tz

def FindUrl(string): 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)       
    return [x[0] for x in url]

headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})

def GetClubhouse(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    
    # title 
    title = soup.find("meta",  property="og:title")["content"]
    #print(title)
    
    # event url 
    url = soup.find("meta",  property="og:url")["content"]
    #print(url)
    
    # date
    PACIFIC = tz.gettz("America/Los_Angeles")
    timezone_info = {"PST": PACIFIC, "PDT": PACIFIC}
    date = soup.find('div', class_='text-gray-600 text-md')
    date = re.sub(' +', ' ', date.text.replace('\n',''))
    date = parser.parse(date, tzinfos=timezone_info)
    #print(date)
    
    # speakers name
    speakers = soup.find('div', class_='px-6 mt-2 italic font-light text-black text-md')
    speakers = [x.strip() for x in speakers.text.replace('w/','').split(',')]
    #print(speakers)
    
    # avatars
    results = soup.find_all('div', class_='flex items-center justify-center')
    avatar_img_urls = FindUrl(str(results))
    #print(avatar_img_urls)
    
    # description
    description = soup.select("div[class='mt-6']")[0].text.strip()
    #print(description)

    event = {"title": title, "url": url, "date" : date.isoformat(), "speakers" : speakers, "avatars" : avatar_img_urls, "description" : description}
    
    return event


# main ;-)

urls = ['https://www.joinclubhouse.com/event/xpeELErv', 'https://joinclubhouse.com/event/M6zw0EbE', 'https://www.joinclubhouse.com/event/mapl9QVM', 'https://www.joinclubhouse.com/event/MwkDw8DB']

events = []

for url in urls:
    events.append(GetClubhouse(url))

with open('_data/events.json', 'w') as outfile:
    json.dump(events, outfile, ensure_ascii=False, indent=2)