


def makeOverviewPage(forge, pagekey):
    pagedef, soup, navlist = forge.makeStarterKit(pagekey)
    select = soup.select_one
    select('title').string = forge.sitesettings['title']
    select('.sitetitle').string = forge.sitesettings['name']
    return {'overviiiiii': str(soup)}
