from json import dumps, loads
from bs4 import BeautifulSoup
import os
import shutil


def defaultPageFn(forge, pagekey):
    "Called when a pagetype doesn't have an associated method regsitered"
    pagebeginning = "<html><head><title>Someone Goofed, "
    pagetype = forge.sitesettings['pages'][pagekey]['type']
    pageend = " doesn't have a function</title></head></html>"
    return {pagekey: pagebeginning + pagetype + pageend}


class WurmForge:
    def __init__(self, siteopts_location, parser='html5lib'):
        self.sitesettings = loads(open(siteopts_location).read())
        self.__default_page_fn__ = defaultPageFn
        self.__pagefns__ = {}
        self.__parser__ = parser

    def defPageMethod(self, pagetype, pagefn):
        """Adds a page method that dispatches on the given pagetype.
        See defaultPageFn() for an example of a valid page method"""
        self.__pagefns__[pagetype] = pagefn
        return self

    def makePage(self, pagekey):
        """Renders the HTML string for a page in the site
        Returns a dict of {url_string, html_string}
        Paramater is the key of the page in sitesettings['pages']
        Defers actual work of converting page defintions to html,
            to functions registered with defPageMethod.
        """
        pagedata = self.sitesettings["pages"][pagekey]
        pagefn = self.__pagefns__.get(pagedata["type"],
                                      self.__default_page_fn__)
        result = pagefn(self, pagekey)
        return result

    def makeBowlOfSoup(self, filename):
        return BeautifulSoup(open("template/" + filename), self.__parser__)

    def makeNavList(self, pageOn):
        siteopts = self.sitesettings
        blankbody = BeautifulSoup('', self.__parser__)
        pageorder = siteopts['pageorder']
        ul = blankbody.new_tag(name='ul')
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

    def setupOutput(self):
        try:
            shutil.rmtree(self.sitesettings['output'])
        except:
            print("No output folder just yet")
        shutil.copytree("template", self.sitesettings['output'])
        return self

    def getSoupFor(filename):
        return BeautifulSoup(open("template/" + filename), __parser)

    def makePages(self):
        result = {}
        for pagekey, pagedata in self.sitesettings['pages'].items():
            madepage = self.makePage(pagekey) 
            result = {**result, **madepage}
        return result 

    def __writePage__(self, filename, pagestring):
        openfile = open(self.sitesettings['output'] + "/" + filename, "w")
        openfile.write(pagestring)
        openfile.close

