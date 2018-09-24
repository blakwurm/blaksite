
class WurmForge:
    def __init__(self, siteopts_location):
        self.sitesettings = loads(open(siteopts_location).read())
        self.__pagefns__ = {"", lambda x: "<html><head><title>Someone Goofed</title></head></html>"}
    
    def makePage(self, pagename):
        return false
