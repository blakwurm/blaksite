from bs4 import BeautifulSoup
from gfm import gfm, markdown


def makeSimplePage(forge, pagekey):
    pagedef, soup = makeStarterKit(forge, pagekey)
    select = soup.select_one
    md1 = strainMarkdown(forge, 'siteintro.md')
    pagemain = select('#pagemain')
    pagemain.clear()
    pagemain.append(md1)
    return {pagedef['url']: str(soup)}

def soupFor(forge, filename):
    with open("template/" + filename) as templatefile:
        return BeautifulSoup(templatefile, __bs4parser__)

def markdownToSoup(markdownstring):
    renderedMarkdown = markdown(gfm(markdownstring))
    newsoup = BeautifulSoup(renderedMarkdown, __bs4parser__)
    container = newsoup.body
    container.name = 'span'
    container['class'] = 'mdrender'
    return container

def strainMarkdown(forge, markdown_location):
    with open(forge.sitesettings['medialocation'] 
            + '/' + markdown_location, 'r') as markdownfile:
        return markdownToSoup(markdownfile.read())

def makeNavList(forge, pageOn):
    siteopts = forge.sitesettings
    blankbody = BeautifulSoup('', __bs4parser__)
    pageorder = forge.sitesettings['pageorder']
    ul = blankbody.new_tag(name='ul')
    ul['class'] = ['navbar']
    for page in pageorder:
        pagedata =forge.sitesettings['pages'][page]
        li = blankbody.new_tag(name='li')
        if pageOn == page:
            li['class'] = ["hello"]
        a = blankbody.new_tag(name='a', href=pagedata['url'])
        a.append(pagedata['title'])
        li.append(a)
        ul.append(li)
    return ul

def makeStarterKit(forge, pagekey, template_filename = 'index.html'):
    soup = soupFor(forge, template_filename)
    navlist = makeNavList(forge, pagekey)
    pagedef = forge.pageInfoFor(pagekey)
    select = soup.select_one
    select('title').string = forge.sitesettings['title']
    select('.sitetitle').string = forge.sitesettings['name']
    select('.navbar').replace_with(navlist)
    return (pagedef, soup)


__bs4parser__ = 'html5lib'
