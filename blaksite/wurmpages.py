from bs4 import BeautifulSoup
from gfm import gfm, markdown

__bs4parser__ = 'html5lib'

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

def strainMarkdown(self, markdown_location):
    with open(self.sitesettings['medialocation'] 
            + '/' + markdown_location, 'r') as markdownfile:
        return markdownToSoup(markdownfile.read())

def makeNavList(self, pageOn):
    siteopts = self.sitesettings
    blankbody = BeautifulSoup('', __bs4parser__)
    pageorder = siteopts['pageorder']
    ul = blankbody.new_tag(name='ul')
    ul['class'] = ['navbar']
    for page in pageorder:
        pagedata = siteopts['pages'][page]
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


def makeSimplePage(forge, pagekey):
    pagedef, soup = makeStarterKit(forge, pagekey)
    select = soup.select_one
    md1 = strainMarkdown(forge, 'siteintro.md')
    pagemain = select('#pagemain')
    pagemain.clear()
    pagemain.append(md1)
    return {pagedef['url']: str(soup)}
