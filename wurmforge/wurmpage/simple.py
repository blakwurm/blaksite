from wurmpages import *

def makeSimplePage(forge, pagekey):
    """Page method for 'simple' page type"""
    for i in forge.prog(['a'], 'Making ' + pagekey):
        pagedef, soup, change = makeStarterKit(forge, pagekey)
        md1 = strainMarkdown(forge, pagedef['source'])
        change('.pagecontent', replaceContents(md1))
        change('.pagetitle', replaceString(pagedef['title']))
        change('.pagesubtitle', replaceString(pagedef['subtitle']))
    return {pagedef['url']: str(soup)}
