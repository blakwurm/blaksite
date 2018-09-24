#!/usr/bin/python3
from json import dumps, loads
from bs4 import BeautifulSoup
import os
import shutil

__parser = 'html5lib'

def getSiteSettings(siteopts_location):
    sitesettings = loads(open(siteopts_location).read())
    return sitesettings 

def grabHTML(filename):
    return BeautifulSoup(open("template/" + filename), __parser)

def changeInnerElement(element, htmlstring):
    #if (element != None):
    #element.clear()
    #element.append(BeautifulSoup(htmlstring, __parser))
    print("htmlstring is " + htmlstring)
    print("element is ")
    print(element)
    element.string.replace_with(BeautifulSoup(htmlstring, __parser))
    return element

def passtest(arg):
    return arg

def makenavlist(siteopts):
    blankbody = BeautifulSoup('', __parser)
    ul = blankbody.new_tag(name ='ul')
    for pagekey, page in siteopts['pages'].items():
        li = blankbody.new_tag(name = 'li')
        a = blankbody.new_tag(name = 'a', href = page['url'])
        a.append(page['title'])
        li.append(a)
        ul.append(li)
    return ul


def makeMainPage(siteopts):
    page = grabHTML("index.html")
    print(page.select_one('title'))
    print(page.select_one('.sitetitle'))
    print(page.select_one('.navbar'))
    page.head.title.string = siteopts['title']
    page.find(class_ = 'sitetitle').string = siteopts['name']
    page.find(class_ = 'sitetagline').string = siteopts['tagline']
    #passtest(page.select_one('.navbar')).string = "<li>doodad</li>"
    navbar = page.find(class_ = 'navbar')
    navbar.clear()
    navbar.append(makenavlist(siteopts))
    #changeInnerElement(page.find(class_ = "navbar"), '<li>doodad</li>'), 
    #changeInnerElement(page.select_one('title'), siteopts['title'])
    #changeInnerElement(page.select_one('.sitetitle'), siteopts['title'])
   # page.find(class_ = "sitetitle").string.replaceWith(siteopts['name'])
    return page

def setupOutput(siteopts):
    try:
        shutil.rmtree(siteopts['output'])
    except:
        print("No output folder just yet")
    shutil.copytree("template", siteopts['output'])
    return siteopts
    
def writePage(siteopts, filename, page):
    openfile = open(siteopts['output'] + "/" + filename, "w")
    openfile.write(page)
    openfile.close

def main(siteopts = "sitesettings.json"):
    setupOutput(getSiteSettings(siteopts))
    print(getSiteSettings(siteopts))
    print(writePage(
        getSiteSettings(siteopts),
        'index.html',
        str(makeMainPage(getSiteSettings(siteopts)))))
    print("page names")
    print(makenavlist(getSiteSettings(siteopts)))

if __name__ == '__main__':
    import plac; plac.call(main)
