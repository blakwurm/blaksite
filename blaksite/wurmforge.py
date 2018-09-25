from json import dumps, loads
from bs4 import BeautifulSoup
import os
import shutil

class WurmForge:
    def __init__(self, siteopts_location, parser = 'html5lib'):
        self.sitesettings = loads(open(siteopts_location).read())
        self.__pagefns__ = {"", lambda self, pagekey : "<html><head><title>Someone Goofed</title></head></html>"}
        self.__parser__ = parser
    
    def defPageMethod(self, pagetype, pagefn):
        __pagefns__[pagetype] = pagefn
        return self

    def makePage(self, pagekey):
        pagedata = self.sitesettings["pages"][pagekey]
        pagefn = __pagefns__[pagedata["type"]]
        result = pagefn(self, pagekey) if (pagefn != None) else __pagefns__[""](self, pagekey)
        return result

    def makeNavList(self, pageOn):
        siteopts = self.sitesettings
        blankbody = BeautifulSoup('', self.__parser__)
        pageorder = siteopts['pageorder']
        ul = blankbody.new_tag(name ='ul')
        for page in pageorder:
            pagedata = siteopts['pages'][page]
            li = blankbody.new_tag(name = 'li') 
            a = blankbody.new_tag(name = 'a', href = pagedata['url'])
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
    


