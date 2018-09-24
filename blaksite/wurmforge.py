
class WurmForge:
    def __init__(self, siteopts_location):
        self.sitesettings = loads(open(siteopts_location).read())
        self.__pagefns__ = {"", lambda self, pagekey : "<html><head><title>Someone Goofed</title></head></html>"}
    
    def defPageMethod(self, pagetype, pagefn):
        __pagefns__[pagetype] = pagefn

    def makePage(self, pagekey):
        pagedata = sitesettings["pages"][pagekey]
        pagefn = __pagefns__[pagedata["type"]]
        pagefn(self, pagekey)
        return pagedata
