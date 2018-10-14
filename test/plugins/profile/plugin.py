from bs4 import BeautifulSoup
from wurmpages import *
import os

def pagemethod(forge, pagekey):
    """Page method for 'simple' page type"""
    for i in forge.prog(['a'], 'Making ' + pagekey):
        pagedef, soup, change = makeStarterKit(forge, pagekey, 'profile.html')
        md1 = strainMarkdown(forge, pagedef['source'])
        change('.pagecontent', replaceContents(md1))
        change('.pagetitle', replaceString(pagedef['title']))
        change('.pagesubtitle', replaceString(pagedef['subtitle']))
        change('.profilepic', replaceProperty('href', pagedef['profilepic']))
    return {pagedef['url']: str(soup)}

