import re
import os
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

#gather bs4 soup from url that will be use for data scraping
#uses web driver + selenium to load scripts to see availabilities instead of just static html
def getSoups(url):
    driver.get(url)
    element = driver.find_element_by_xpath('//*')
    html = element.get_attribute('innerHTML')
    soup = BeautifulSoup(html, 'lxml')
    return soup

class Msy:
    #information to be collected Model Availability Price and Location
    def __init__(self, soup):
        self.soup = soup
        self.rtxlist = {
            'model': [],
            'availability': [],
            'price': [],
            'location': [],
        }

        #MSY doesnt show availability on search page thus need to go through each search items link thus 
        #the need to using basepage plus collecting further links for each item
        self.msybaseurl = "https://www.msy.com.au"
        self.msylinks = []

    #main scrapping function
    def getAllInformation(self):
        soup = self.soup
        itemlist = soup.html.body.findAll("h2",{"class":"product-title"})
        for x in itemlist:
            #gets individual link to check more information
            item=x.get_text('a',{"href":True})
            itemlink = self.msybaseurl + x.find('a').get('href') + "#stock-availability"
            self.rtxlist['model'].append(item)
            #stores individual links for future reference + checking
            self.msylinks.append(itemlink)
            #gets soup for new links
            singlesoup = getSoups(itemlink)
            #gets more information need in the new links
            self.itemInfo(singlesoup)

    #prints RTX information
    def printRTX(self):
        indexlist = self.getRTXindices()
        for x in indexlist:
            print(f"MSY Model: {self.rtxlist['model'][x]:<100s} Price {self.rtxlist['price'][x]:>7s} Location: {self.rtxlist['location'][x]} {self.rtxlist['availability'][x]:>10}")

    #returns a list of indices of rtx gpus
    def getRTXindices(self):
        patternName = re.compile('^((?!backplate|Corsair|Vector).)*$',re.IGNORECASE)
        ilist = []
        counter = 0
        for x in self.rtxlist['model']:
            if bool(re.search(patternName,x))==True:
                ilist.append(counter)
            counter+=1
        return ilist
        
    #getting price availability location in individual links of msy site
    def itemInfo(self,soup):
        price = soup.html.body.find("span",{"class":re.compile("price")}).get("content")
        availability = soup.html.body.findAll("tr",{"class":"even"})
        location = availability[-1].find('td').get_text().strip()
        availabilityItem = availability[-1].findAll('td')[-1].get_text().strip()
        self.rtxlist['price'].append(price)
        self.rtxlist['availability'].append(availabilityItem)
        self.rtxlist['location'].append(location)


class Ple:
    #information to be collected Model Availability Price and Location
    def __init__(self, soup):
        self.soup = soup
        self.rtxlist = {
            'model': [],
            'availability': [],
            'price': [],
            'location': [],
        }

    #main scrapping function
    def getAllInformation(self):
        soup = self.soup
        itemlist = soup.html.body.findAll("div", class_="itemGridTileDescription")
        for x in itemlist:
            self.rtxlist['model'].append(x.text)
        pricelist = soup.html.body.findAll("span", class_="itemGridTilePriceActual")
        for x in pricelist:
            self.rtxlist['price'].append(x.text)
        availabilitylist = soup.html.body.findAll("div",{'class':"itemGridTileAvailabilityItem"})
        counter=0
        for x in availabilitylist:
            if counter%2<1:
                availability = x.text.split('Western Australia')[0]
                self.rtxlist['location'].append('Western Australia')
                self.rtxlist['availability'].append(availability)
            if x.text=='Ordered as required':
                counter+=1
            counter+=1

    #returns a list of indices of rtx gpus
    def printRTX(self):
        indexlist = self.getRTXindices()
        for x in indexlist:
            print(f"PLE Model: {self.rtxlist['model'][x]:<60s} Price {self.rtxlist['price'][x]:>7s} Location: {self.rtxlist['location'][x]} {self.rtxlist['availability'][x]:>10}")

    #returns a list of indices of rtx gpus
    def getRTXindices(self):
        patternName = re.compile('^((?!backplate|PC|Corsair|Vector|System|Bykski).)*$',re.IGNORECASE)
        ilist = []
        counter = 0
        for x in self.rtxlist['model']:
            if bool(re.search(patternName,x))==True:
                ilist.append(counter)
            counter+=1
        return ilist

"""
Main program
"""

#url to check PLE and MSY
search = ['RTX 3060','RTX 3070','RTX 3080','RTX 3090']
baseUrl = ['https://www.ple.com.au/Search/','https://www.msy.com.au/search?q=']

#will call urllist and proper scraping function 
for keyword in search:
    for url in baseUrl:
        links = url + keyword
        soup = getSoups(links)
        if re.search('ple',links):
            model = links.split('/')
            print(f"\n{model[-1]}")
            ple =  Ple(soup)
            ple.getAllInformation()
            ple.printRTX()
        else:
            model = links[-4:]
            print(f"\nRTX {model}")
            msy =  Msy(soup)
            msy.getAllInformation()
            msy.printRTX()
driver.close()
os.system('pause')