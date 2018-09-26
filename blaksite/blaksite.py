#!/usr/bin/python3
from json import dumps, loads
from bs4 import BeautifulSoup
import os
import shutil
from wurmforge import WurmForge

__parser = 'html5lib'

def main(siteopts = "sitesettings.json"):
    forge = WurmForge(siteopts)
    forge.makeSite()
    print(forge)
    print(forge.sitesettings['pages'])
    print(forge.makeNavList('Home'))
    print(forge.makePages())
    print("page names")

if __name__ == '__main__':
    import plac; plac.call(main)
