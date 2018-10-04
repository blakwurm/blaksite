#!/usr/bin/python3
from wurmforge import WurmForge
from pprint import PrettyPrinter
from wurmpages import makeSimplePage, makeBlogPage

def main(siteopts = "sitesettings.json", debug:('prints more info', 'flag', 'd') = False):
    pp = PrettyPrinter()
    forge = WurmForge(siteopts)
    forge.debug_flag = debug
    forge.defPageMethod('simple', makeSimplePage)
    forge.defPageMethod('blog', makeBlogPage)
    forge.makeSite()
    #pp.pprint(forge.strainMarkdown('siteintro.md'))
    if debug:
        forge.debug_flag = debug
        pp.pprint(forge.makePages())

if __name__ == '__main__':
    import plac; plac.call(main)
