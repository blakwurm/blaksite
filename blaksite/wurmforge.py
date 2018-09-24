
class WurmForge:
    def __init__(self, siteopts_location):
        self.sitesettings = loads(open(siteopts_location).read())
        self.__pagefns__ = {"", lambda self, pagekey : "<html><head><title>Someone Goofed</title></head></html>"}
    
    def defPageMethod(self, pagetype, pagefn):
        __pagefns__[pagetype] = pagefn
        return self

    def makePage(self, pagekey):
        pagedata = sitesettings["pages"][pagekey]
        pagefn = __pagefns__[pagedata["type"]]
        result = pagefn(self, pagekey) if (pagefn != None) else __pagefns__[""](self, pagekey)
        return result

    def makeNavList(self, pageon = "index"):
        pagenames = list(map(lambda x: x['title'], siteopts['pages']))
        blankbody = BeautifulSoup('', __parser)
        ul = blankbody.new_tag(name ='ul')
        for page in siteopts['pages']:
            li = blankbody.new_tag(name = 'li', class_ = "thispage" if (page == pageon) else "")
            a = blankbody.new_tag(name = 'a', href = page['url'])
            a.append(page['title'])
            li.append(a)
            ul.append(li)
        return ul

    def getSoupFor(filename):
        return BeautifulSoup(open("template/" + filename), __parser)
    


