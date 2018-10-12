#!/usr/bin/python3
from wurmforge import WurmForge
from pprint import PrettyPrinter
from wurmpage.blog import makeBlogPage
from wurmpage.simple import makeSimplePage
from wurmpage.external import makeExternalPage
from contextlib import contextmanager
from os import getcwd, path, chdir

def main(workingdir = ".", debug:('prints more info', 'flag', 'd') = False):
    try:
        with cd(workingdir):
            siteopts = "sitesettings.json"
            forge = WurmForge(siteopts)
            forge.debug_flag = debug
            forge.defPageMethod('simple', makeSimplePage)
            forge.defPageMethod('blog', makeBlogPage)
            forge.defPageMethod('external', makeExternalPage)
            forge.makeSite()
    #pp.pprint(forge.strainMarkdown('siteintro.md'))
            if debug:
                pp = PrettyPrinter()
                forge.debug_flag = debug
                #pp.pprint(forge.makePages())
    except FileNotFoundError as err:
        if debug:
            raise err
        else:
            print("Critical Failure. File Not Found: " + str(err.filename))
            print("For more details, see https://github.com/blakwurm/blaksite")
    except Exception as err:
        if debug:
            raise err
        else:
            print("Critical Failure. Something went wrong.")
            print("For more details, see https://github.com/blakwurm/blaksite")

@contextmanager
def cd(newdir):
    "https://stackoverflow.com/questions/431684/how-do-i-change-directory-cd-in-python/24176022#24176022"
    prevdir = getcwd()
    chdir(path.expanduser(newdir))
    try:
        yield
    finally:
        chdir(prevdir)

if __name__ == '__main__':
    import plac; plac.call(main)
