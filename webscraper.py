import requests
from bs4 import BeautifulSoup
import json

for year in range(2006,2020):
    year = str(year)
    URL = "https://www.billboard.com/charts/year-end/"+year+"/hot-100-songs"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    result = soup.find_all("div", class_='ye-chart-item__text')

    rank = 1
    data = {}

    for res in result:
        song = res.find("div", class_="ye-chart-item__title")
        artist = res.find("div",class_="ye-chart-item__artist")

        if None in (song, artist):
            continue

        stext = song.text.strip()
        atext = artist.text.strip()

        #print(rank," ", stext, " ", atext)
        data[rank] = []
        data[rank].append({
            'artist' : atext,
            'song' : stext
        })

        rank += 1

    with open("data/data"+year+".txt", "w+") as outfile:
        json.dump(data, outfile)