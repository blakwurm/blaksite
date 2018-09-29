


def makeSimplePage(forge, pagekey):
    pagedef, soup, navlist = forge.makeStarterKit(pagekey)
    select = soup.select_one
    select('title').string = forge.sitesettings['title']
    select('.sitetitle').string = forge.sitesettings['name']
    select('.navbar').replace_with(navlist)
    md1 = forge.strainMarkdown('siteintro.md')
    pagemain = select('#pagemain')
    pagemain.clear()
    pagemain.append(md1)
    return {pagedef['url']: str(soup)}
