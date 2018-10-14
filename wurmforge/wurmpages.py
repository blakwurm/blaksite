from bs4 import BeautifulSoup
from gfm import gfm, markdown
from json import dumps, loads
from copy import copy
from urllib.parse import quote, urlparse
import re
from contextlib import suppress
from itertools import tee, islice, chain
from datetime import datetime
from functools import partial

def makeMediaLink(forge, filename):
    """Makes a path to a file in the medialocation"""
    return forge.settingFor('medialocation') + "/" + "filename"

def templateSoupFor(forge, filename):
    """Returns a new bs4 element for a file in /template/html"""
    with open(forge.settingFor('templatelocation') + "/html/" + filename) as templatefile:
        return BeautifulSoup(templatefile, bs4parser)

def removeSpecialChars(stringToChange):
    """Given a string, removes all non-alphanumeric characters"""
    reg = re.compile('[^a-zA-Z0-9]')
    return reg.sub('', stringToChange)

def markdownToSoup(markdownstring):
    """Takes a string of markdown, and returns a rendered bs4 element"""
    renderedMarkdown = markdown(gfm(markdownstring))
    newsoup = BeautifulSoup(renderedMarkdown, bs4parser)
    container = newsoup.body
    container.name = 'span'
    container['class'] = 'mdrender'
    return container

def strainMarkdown(forge, markdown_location):
    """Grabs markdown from markdown_location, and returns the result of passing it to markdownToSoup()"""
    with open(forge.settingFor('medialocation') 
            + '/' + markdown_location, 'r') as markdownfile:
        return markdownToSoup(markdownfile.read())

def makeNavList(forge, pageOn):
    """Returns a bs4 ul top-level navigation element equivilant to
    <ul>
        <li><a href="/path/to/page">Page Name</a></li>
    </ul>"""
    siteopts = forge.sitesettings
    blankbody = BeautifulSoup('', bs4parser)
    pageorder = forge.settingFor('pageorder')
    ul = blankbody.new_tag(name='ul')
    #ul['class'] = ['navbar']
    for pagekey in pageorder:
        pagedata =forge.pageInfoFor(pagekey)
        li = blankbody.new_tag(name='li')
        if pageOn == pagekey:
            li['class'] = ["hello"]
        a = blankbody.new_tag(name='a', href=__makeNavbarUrl(pagedata['url']))
        a.append(pagedata['title'])
        li.append(a)
        ul.append(li)
    return ul

def __makeNavbarUrl(urlstring):
    parsed = urlparse(urlstring)
    return urlstring if parsed.scheme or parsed.netloc else '/' + urlstring

def makePageTitle(forge, pagekey):
    """Returns the computed page title for use in <title>"""
    return forge.settingFor('title') +\
        forge.settingFor('titledelimiter') +\
        forge.pageInfoFor(pagekey).get('title')

def makeStarterKit(forge, pagekey, template_filename = 'index.html'):
    """Executes boilerplate common to every page method
    
    Returns a 3-tuple of the page definition,
    the root soup object,
    and __change partially applied with the root soup"""
    soup = templateSoupFor(forge, template_filename)
    navlist = makeNavList(forge, pagekey)
    pagedef = forge.pageInfoFor(pagekey)
    change = partial(change_element, soup)
    dt = datetime.now()
    #select('title').string = makePageTitle(forge, pagekey)
    change('title', replaceString(makePageTitle(forge, pagekey)))
    change('.sitetitle', replaceString(forge.sitesettings['name']))
    change('.sitetagline', replaceString(forge.sitesettings['tagline']))
    change('a.rootlink', replaceHref('/' + forge.pageInfoFor('Home')['url']))
    change('.navbar ul', replaceWith(navlist))
    copyrightholder = forge.settingFor('copyrightholder', 'name')
    change('.copyright', replaceString('(c) ' + str(dt.year) + ' ' + copyrightholder))
    return (pagedef, soup, change)

def change_element(soup, selector, deltafn):
    """Convienence function to make *safely* changing a group of elements a one-liner

    Keyword Arguments:
    soup -- The parent bs4 element on which .select or .select_one will be called
    selector -- String css selector that selects a group of elements
    deltafn -- Function accepting a single element, that mutates the element as desired"""
    try :
        select = soup.select
        elements = select(selector)
        for element in elements:
            deltafn(element)
    except Exception as exp:
        print("Non-fatal problem: " + str(exp))

def replaceContents(newContents):
    """For use with change_element, shortcut for clearing and then appending on an element"""
    def retFn(element):
        element.clear()
        element.append(newContents)
    return retFn

def replaceWith(replacement):
    def retFn(element):
        element.replaceWith(replacement)
    return retFn

def replaceString(newString):
    """For use with change_element, shortcut for replacing the .string on an element"""
    def retFn(element):
        element.string.replaceWith(newString)
    return retFn

def replaceHref(newHref):
    """For use with change_element, shortcut for replacing the ['href'] on an element"""
    def retFn(element):
        element['href'] = newHref
    return retFn

def appendWith(additionalElement):
    """For use with change_element, shortcut for calling .append(additionalElement) on an element"""
    def retFn(element):
        element.append(additionalElement)
    return retFn


"""As html5lib does things a bit differently then other html parsers,
changing this is not advised without rewriting some of the functions in this module"""
bs4parser = 'html5lib'
