from bs4 import BeautifulSoup
import requests
import re
import datetime
import json
import os
import validators
from dateutil import parser
from dateutil import tz
from datetime import datetime, timedelta
import pytz
from github import Github
from airtable import Airtable


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
    
    # event url 
    url = soup.find("meta",  property="og:url")["content"]
    
    # date
    PACIFIC = tz.gettz('America/Los_Angeles')
    to_zone = tz.gettz('Europe/Warsaw')
    timezone_info = {"PST": PACIFIC, "PDT": PACIFIC}
    date = soup.find('div', class_='text-gray-600 text-md')
    date = re.sub(' +', ' ', date.text.replace('\n',''))
    date = parser.parse(date, tzinfos=timezone_info)
    date = date.astimezone(to_zone)
    
    # speakers name
    speakers = soup.find('div', class_='px-6 mt-2 italic font-light text-black text-md')
    speakers = [x.strip() for x in speakers.text.replace('w/','').split(',')]
    
    # avatars
    results = soup.find_all('div', class_='flex items-center justify-center')
    avatar_img_urls = FindUrl(str(results))
    
    # description
    description = soup.select("div[class='mt-6']")[0].text.strip()

    event = {"title": title, "url": url, "date" : date.isoformat(), "speakers" : speakers, "avatars" : avatar_img_urls, "description" : description}
    
    return event


# main ;-)
urls = []

g = Github(os.getenv('GITHUB_TOKEN'))

repo = g.get_repo("kaluzaaa/clubhouse-calendar")
open_issues = repo.get_issues(state='open')
for issue in open_issues:
    if validators.url(issue.title):
        urls.append(issue.title)

airtable = Airtable(os.getenv('AT_BASE_ID'), 'Auditions', os.getenv('AT_API_KEY'))

for item in airtable.get_all(fields='URL'):
    urls.append(item['fields']['URL'])

urls = list(dict.fromkeys(urls))

events = []

for url in urls:
    events.append(GetClubhouse(url))

with open('_data/events.json', 'w') as outfile:
    json.dump(events, outfile, ensure_ascii=False, indent=2)

for event in events:
    update = airtable.update_by_field('URL', event['url'], {'Hosts': ', '.join(event['speakers']), 'Description' : event['description'], 'Audition Name' : event['title']})
    if not update:
        insert = airtable.insert({'URL' : event['url'], 'Hosts': ', '.join(event['speakers']), 'Description' : event['description'], 'Audition Name' : event['title']})
        print('Insert: ',insert)
    else:
        print('Update: ', update)

# close old issue

now = datetime.now(pytz.utc)
for issue in open_issues:
    if validators.url(issue.title):
        for event in events:
            if event['url'] == issue.title:
                if parser.parse(event['date']) + timedelta(hours=4) < now:
                    issue.edit(state='closed')