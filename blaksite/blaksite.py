#!/usr/bin/python3
from wurmforge import WurmForge
from pprint import PrettyPrinter

__parser = 'html5lib'

def main(siteopts = "sitesettings.json"):
    pp = PrettyPrinter()
    forge = WurmForge(siteopts)
    forge.makeSite()
    pp.pprint(forge.strainMarkdown('siteintro.md'))
    # pp.pprint(forge.makePages())

if __name__ == '__main__':
    import plac; plac.call(main)
