from json import dumps, loads
from shutil import rmtree, copytree
from pathlib import Path, PurePath
from distutils.dir_util import copy_tree
from progressbar import progressbar
from contextlib import contextmanager


def defaultPageFn(forge, pagekey):
    "Called when a pagetype doesn't have an associated method regsitered"
    pagebeginning = "<html><head><title>Someone Goofed, "
    pagetype = forge.sitesettings['pages'][pagekey]['type']
    pageend = " doesn't have a function</title></head></html>"
    urlstring = forge.sitesettings['pages'][pagekey]['url']
    return {urlstring: pagebeginning + pagetype + pageend}


class WurmForge:
    debugFlag = False

    def __init__(self, siteopts_location):
        with open(siteopts_location) as siteopts_file:
            sitesettings_tmp = loads(siteopts_file.read())
            self.sitesettings = {**self.__sitesettings_defaults__,
                                 **sitesettings_tmp}
            self.__default_page_fn__ = defaultPageFn
            self.__pagefns__ = {}
            self.__parser__ = 'html5lib' 
            self.__tmpoutput__ = 'blaktmp'

    """Software version, accessable to plugins. Versions under 1.0 are considered alpha."""
    version = 0.1

    def prog(self, seq, desc): 
        """Takes an iterable and a description, returns an iterable that
        renders a progress bar to the command line."""
        print(desc)
        return progressbar(seq)

    @contextmanager
    def prog_one(self, message):
        """Renders a 1-item progress bar on the screen when block exits"""
        for i in self.prog(['a'], message):
            yield

    def defPageMethod(self, pagetype, pagefn):
        """Adds a page method that dispatches on the given pagetype.
        See defaultPageFn() for an example of a valid page method"""
        self.__pagefns__[pagetype] = pagefn
        return self

    def getPageMethod(self, pagetype):
        "Returns the function for the corresponding pagetype"
        return self.__pagefns__.get(pagetype,
                                    self.__default_page_fn__)

    def makePage(self, pagekey):
        """Renders the HTML string for a page in the site
        Returns a dict of {url_string, html_string}
        Paramater is the key of the page in sitesettings['pages']
        Defers actual work of converting page defintions to html,
            to functions registered with defPageMethod.
        """
        pagedata = self.sitesettings["pages"][pagekey]
        pagefn = self.getPageMethod(pagedata["type"])
        result = pagefn(self, pagekey)
        return result


    def pageInfoFor(self, pagekey):
        """Shortcut for forge.settingFor('page').get(pagekey)"""
        return self.sitesettings['pages'].get(pagekey, {})

    def settingFor(self, thingkey, altkey = 'name'):
        """Shortcut for safely getting a site setting with an alternate."""
        return self.sitesettings.get(thingkey,
                self.sitesettings.get(altkey, ''))

    def setupOutput(self):
        """Prepares the temp output directory for writing"""
        copytree(self.settingFor('templatelocation'), self.__tmpoutput__) 
        rmtree(self.__tmpoutput__ + "/html")
        #copytree(self.settingFor('assetlocation'), self.__tmpoutput__)
        return self

    def cleanupOutput(self):
        """Merges the temp output directory with the target directory,
        and deletes the temp directory"""
        copy_tree(self.__tmpoutput__, self.sitesettings['output'])
        copy_tree(self.settingFor('assetlocation'), self.settingFor('output'))
        try:
            rmtree(self.__tmpoutput__)
        except:
            if self.debugFlag:
                print("Something is wrong.")
        pass

    def makePages(self):
        """Returns a dict of {path-relative-to-site-root, document-string},
        where paths ending without a filename are assumed to be directories
        out of which index.html will be served"""
        result = {}
        for pagekey, pagedata in self.sitesettings['pages'].items():
            madepage = self.makePage(pagekey) 
            result = {**result, **madepage}
        return result 

    def makeSite(self):
        """Builds the site dict per forge.makePages,
        and outputs it to sitesettings['output']"""
        pages = self.makePages()
        self.setupOutput()
        for urlstring, htmlstring in self.prog(pages.items(), 'Writing Pages'):
            urlpath = PurePath(urlstring)
            filename = urlpath.name if urlpath.suffix else 'index.html'
            writepath = str(urlpath.parent) if urlpath.suffix else urlstring
            self.__writePage__(file_path = writepath, 
                               file_name = filename,
                               page_string = htmlstring)
        self.cleanupOutput()
        return self

    def __writePage__(self, file_path, file_name, page_string):
        """Writes an individual page"""
        true_file_path = self.__tmpoutput__ + '/' + file_path
        true_file_name = true_file_path + '/' + file_name
        Path(true_file_path).mkdir(parents=True, exist_ok=True)
        Path(true_file_name).touch(exist_ok=True)
        with open(true_file_name , "w+") as openfile:
            openfile.write(page_string)

    __sitesettings_defaults__ = \
            {'name': 'Unnamed Site',
             '': '',
             'title': 'Untitled Site',
             'tagline': 'Catchy Tagline!',
             'output': 'docs',
             'medialocation': 'media',
             'templatelocation': 'template',
             'assetlocation': 'assets',
             'name': 'Blaksite Default',
             'tagling': 'Insert tagline here',
             'title': 'This title is fun!',
             'address': '',
             'titledelimiter': ' - '}
