import requests
from bs4 import BeautifulSoup
from dbElastic import dbElastic


class exportWeb:
    def __init__(self, url, tCount):
        self.tCount = tCount
        self.urlUser = url
        url = f"{url.split('/')[0]}//{url.split('/')[2]}"
        self.url = url
        urlSearch = self.__searchDB(url)
        if urlSearch:
            self.__getPars()

    @staticmethod
    def __getRequest(urlItem):
        counter = 0
        statuscode_link = 400
        while True:
            try:
                response = requests.request("GET", urlItem, headers={'User-Agent': 'PostmanRuntime/7.37.3'}, data={}, timeout=20)
                statuscode_link = response.status_code
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return [soup, statuscode_link]
            except:
                if counter == 3:
                    # print(f"Error {urlItem} statusCode= {statuscode_link}")
                    return [None, statuscode_link]
                else:
                    counter += 1
                continue
            else:
                if counter == 3:
                    # print(f"Error {urlItem} statusCode= {statuscode_link}")
                    return [None, statuscode_link]
                else:
                    if 'https://app.' in urlItem:
                        urlItem = urlItem.replace('https://app.', 'https://')
                    counter += 1
                pass

    def __getPars(self):
        soupHome = self.__getRequest(self.url)
        soupLinkUser = self.__getRequest(self.urlUser)
        if soupHome[1] == 200:
            soup = soupHome[0]
            try:
                url = soup.find('link', {'rel': 'canonical'}).get('href')
                url = f"{url.split('/')[0]}//{url.split('/')[2]}"
            except:
                url = self.url
            title = ""
            if soup.find('title'):
                title = soup.find('title').text
            allLinkData = soup.findAll('a')
            allLinkData.extend(soup.findAll('link'))
            allLinkIn = []
            allLinkOut = []
            for i in allLinkData:
                if i.get("href"):
                    link = (i.get("href")).lower()
                    if not (link in allLinkIn) and not (link in allLinkOut):
                        if (link != "#") and (link != url):
                            if str(link[:2]) == "//":
                                allLinkOut.append(link)
                            elif (url in link) or ((str(link[:2]) != "//") and not (link.split('://')[0] in ['https', 'http'])):
                                allLinkIn.append(link)
                            else:
                                allLinkOut.append(link)
            dataDB = {'url': url, 'statuscode_url': soupHome[1], 'title': title, 'urlUser': self.urlUser, 'statuscode_urlUser': soupLinkUser[1], 'pageSource_Home': str(soupHome[0]), 'pageSource_urlUser': str(soupLinkUser[0]), 'listLinkIn': allLinkIn, 'listLinkOut': allLinkOut}
            self.__getDB(dataDB)
        else:
            dataDB = {'url': self.url, 'statuscode_url': soupHome[1], 'title': None, 'urlUser': self.urlUser, 'statuscode_urlUser': soupLinkUser[1], 'pageSource_Home': str(soupHome[0]), 'pageSource_urlUser': str(soupLinkUser[0]), 'listLinkIn': [], 'listLinkOut': []}
            self.__getDB(dataDB)

    def __searchDB(self, u):
        dbES = dbElastic({'url': u})
        dataSearch = dbES.searchDB()
        if len(dataSearch) == 0:
            return True
        else:
            print(f"url: {self.urlUser}, add in DB: {False}, counter url: {self.tCount}")
            return False

    def __getDB(self, data):
        dataSearch = self.__searchDB(data['url'])
        if dataSearch:
            insES = dbElastic(data)
            print(f"url: {self.urlUser}, add in DB: {insES.insertDB()}, counter url: {self.tCount}")
