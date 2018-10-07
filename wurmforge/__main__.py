#!/usr/bin/python3
from wurmforge import WurmForge
from pprint import PrettyPrinter
from wurmpages import makeSimplePage, makeBlogPage

def main(siteopts = "sitesettings.json", debug:('prints more info', 'flag', 'd') = False):
    try:
        forge = WurmForge(siteopts)
        forge.debug_flag = debug
        forge.defPageMethod('simple', makeSimplePage)
        forge.defPageMethod('blog', makeBlogPage)
        forge.makeSite()
    #pp.pprint(forge.strainMarkdown('siteintro.md'))
        if debug:
            pp = PrettyPrinter()
            forge.debug_flag = debug
            pp.pprint(forge.makePages())
    except FileNotFoundError as err:
        print("Critical Failure. File Not Found: " + str(err.filename))
        print("For more details, see https://github.com/blakwurm/blaksite")

if __name__ == '__main__':
    import plac; plac.call(main)
