from bs4 import BeautifulSoup
from gfm import gfm, markdown
from json import dumps, loads
from copy import copy
from urllib.parse import quote
from re import compile
from contextlib import suppress
from itertools import tee, islice, chain
from datetime import datetime
from functools import partial

def makeSimplePage(forge, pagekey):
    """Page method for 'simple' page type"""
    for i in forge.prog(['a'], 'Making ' + pagekey):
        pagedef, soup, change = makeStarterKit(forge, pagekey)
        md1 = strainMarkdown(forge, pagedef['source'])
        change('.pagecontent', replaceContents(md1))
        change('.pagetitle', replaceString(pagedef['title']))
        change('.pagesubtitle', replaceString(pagedef['subtitle']))
    return {pagedef['url']: str(soup)}

def makeBlogPage(forge, pagekey):
    """Page method for 'blog' page type"""
    pagedef, soup, change = makeStarterKit(forge, pagekey)
    rendermap = {}
    posts = grabBlogPosts(forge, pagekey)
    posts.sort(key = lambda x: x['date'], reverse = True)
    tags = getTagsIn(forge, posts)
    pagedef['tags'] = tags
    for formerpost, post, nextpost \
            in previous_and_next(forge.prog(posts,
                'Making ' + pagekey + ' post pages')):
        rendermap.update(makeBlogPost(forge, pagekey, post, formerpost, nextpost))
    for tag in forge.prog(tags, 'Making ' + pagekey + ' tag pages'):
        rendermap.update(makeBlogOverview(forge,
            pagekey,
            postsWithTag(posts, tag),
            makeBlogTagURL(forge, pagekey, tag)))
    rendermap.update(makeBlogOverview(forge, pagekey, postsWithoutTag(posts, pagedef["hidetag"])))
    return rendermap

def makeBlogTagURL(forge, pagekey, tag):
    """Returns a computed url for a posts summary for a given tag"""
    return forge.pageInfoFor(pagekey)['url'] + '/tag/' + tag

def makeBlogPost(forge, pagekey,
        postdef = {},
        formerpostdef = {},
        nextpostdef = {}):
    """Creates the page for a blog post. Returns a dictionary {'url': 'htmlstring'}
    
    Keyword args:
    forge -- WurmForge instance governing the site's creation
    pagekey -- key pointing to page definition in sitesettings.json > pages
    postdef -- Post definition from posts.json
    formerpostdef -- Immediately previous definition from posts.json
    nextpostdef -- Next post definition from posts.json"""
    pagedef, soup, change = makeStarterKit(forge, pagekey, 'blogpost.html')
    soup.head.title.string += " - " + postdef['title']
    pagetitle = postdef['title']
    change('.taglist ul', replaceContents(makeTagUL(forge, pagekey, pagedef['tags'])))
    with suppress(Exception):
        h1 = postdef['soup'].h1.extract()
        pagetitle = h1.string
    tagul = makeTagUL(forge, pagekey, postdef['tags'])
    change('.taglist ul', replaceWith(tagul))
    change('.pagetitle', replaceString(pagetitle))
    change('.pagecontent', replaceContents(postdef['soup']))
    change('.previouspost', replaceHref(formerpostdef['url'] if formerpostdef else postdef['url']))
    change('.nextpost', replaceHref(nextpostdef['url'] if nextpostdef else postdef['url']))
    change('.postdate', replaceString(postdef['date']))
    return {postdef['url']: str(soup)}

def postsWithTag(posts, tag):
    """Returns all the posts with a given tag"""
    return [post for post in posts if tag in post['tags']]

def postsWithoutTag(posts, tag):
    """Returns all the posts without a given tag"""
    return [post for post in posts if tag not in post['tags']]

def getTagsIn(forge, posts):
    """Returns a list of tags in a list of posts"""
    retList = []
    for post in forge.prog(posts, 'Getting tags from posts'):
        retList.extend(post['tags'])
    return retList

def makeBlogOverview(forge, pagekey, posts = [], url = ''):
    """Creates an overview page for a given blog.
    
    Keyword args:
    forge -- WurmForge instance governing the site's creation
    pagekey -- Key pointing to the page in sitesettings.json > 'pages'
    posts -- List of post definitions from posts.json
    url -- URL of the site relative to the site root"""
    pagedef, soup, change = makeStarterKit(forge, pagekey, "blogsummary.html")
    trueurl = url or pagedef['url']
    change('.taglist ul', replaceWith(makeTagUL(forge, pagekey, pagedef['tags'])))
    previewtemplate = soup.select_one('.postpreview').extract()
    for post in posts:
        slot = ___makeBlogOverviewSlot(forge, pagekey, post, copy(previewtemplate))
        change('.pagecontent', appendWith(slot))
    return {trueurl : str(soup)}

def ___makeBlogOverviewSlot(forge, pagekey, post, template):
    pagedef = forge.pageInfoFor(pagekey)
    change = partial(change_element, template)
    change('.posttitle', replaceString(post['title']))
    change('.byline', replaceString(post['author']))
    change('.date', replaceString(post['date']))
    change('.preview', replaceString(str(post['soup'].p.string)))
    change('.tags', replaceWith(makeTagUL(forge, pagekey, post['tags'])))
    change('.continue', replaceHref(post['url']))
    return template

def makeMediaLink(forge, filename):
    """Makes a path to a file in the medialocation"""
    return forge.settingFor('medialocation') + "/" + "filename"

def templateSoupFor(forge, filename):
    """Returns a new bs4 element for a file in /template"""
    with open("template/" + filename) as templatefile:
        return BeautifulSoup(templatefile, __bs4parser__)

def grabBlogPosts(forge, pagekey):
    """Processes the posts.json for a blog page, and returns the fully processed posts"""
    pagesettings = forge.pageInfoFor(pagekey)
    postspath = pagesettings['postslocation']
    mediapath = forge.sitesettings['medialocation']
    postslocation = mediapath + '/' + postspath 
    postsdefs = getPostDefs(postslocation)
    for postdef in forge.prog(postsdefs, 'Processing ' + pagekey + ' posts'):
        processPostDef(postslocation, pagesettings, postdef)
    return postsdefs

def removeSpecialChars(stringToChange):
    """Given a string, removes all non-alphanumeric characters"""
    reg = compile('[^a-zA-Z0-9]')
    return reg.sub('', stringToChange)
        
def makePostUrl(pagedef, postdef):
    """Given a pagedef from sitesettings.json, and a postdef from posts.json, returns the site url to a post"""
    return '/' + pagedef['url'] + '/post/' +\
            postdef['date'] + '/' + removeSpecialChars(postdef['title'])

def processPostDef(postslocation, pagedef, postdef):
    """Adds url and rendered markdown to a post def
    
    Keyword args:
    postslocation -- Path to the directory with the posts.json that postdef was taken from
    pagedef -- Page definition from sitesettings.json, that the posts fall under
    postdef -- Post definition from posts.json"""
    with open(postslocation + "/" + postdef['source']) as mdfile:
        postSoup = markdownToSoup(mdfile.read())
        postdef['soup'] = postSoup
        postdef['url'] = makePostUrl(pagedef, postdef)
        return postdef

def getPostDefs(postslocation):
    """Given the path to a directory with a posts.json, returns the post information"""
    with open(postslocation + '/' + 'posts.json') as postsdef:
        return loads(postsdef.read())

def markdownToSoup(markdownstring):
    """Takes a string of markdown, and returns a rendered bs4 element"""
    renderedMarkdown = markdown(gfm(markdownstring))
    newsoup = BeautifulSoup(renderedMarkdown, __bs4parser__)
    container = newsoup.body
    container.name = 'span'
    container['class'] = 'mdrender'
    return container

def strainMarkdown(forge, markdown_location):
    """Grabs markdown from markdown_location, and returns the result of passing it to markdownToSoup()"""
    with open(forge.settingFor('medialocation') 
            + '/' + markdown_location, 'r') as markdownfile:
        return markdownToSoup(markdownfile.read())

def makeNavList(forge, pageOn):
    """Returns a bs4 ul top-level navigation element equivilant to
    <ul>
        <li><a href="/path/to/page">Page Name</a></li>
    </ul>"""
    siteopts = forge.sitesettings
    blankbody = BeautifulSoup('', __bs4parser__)
    pageorder = forge.settingFor('pageorder')
    ul = blankbody.new_tag(name='ul')
    #ul['class'] = ['navbar']
    for pagekey in pageorder:
        pagedata =forge.pageInfoFor(pagekey)
        li = blankbody.new_tag(name='li')
        if pageOn == pagekey:
            li['class'] = ["hello"]
        a = blankbody.new_tag(name='a', href='/' + pagedata['url'])
        a.append(pagedata['title'])
        li.append(a)
        ul.append(li)
    return ul

def makeTagUL(forge, pagekey, tags):
    """Returns a bs4 ul element equivilant to
    <ul class="tags">
        <li><a href="/path/to/tag/summary">Tag Name</a></li>
    </ul>"""
    blankbody = BeautifulSoup('', __bs4parser__)
    ul = blankbody.new_tag(name='ul')
    ul['class'] = ['tags']
    for tag in tags:
        li = blankbody.new_tag(name='li')
        url = makeBlogTagURL(forge, pagekey, tag)
        a = blankbody.new_tag(name='a', href='/' + url)
        a.append(tag)
        li.append(a)
        ul.append(li)
    return ul

def makePageTitle(forge, pagekey):
    """Returns the computed page title for use in <title>"""
    return forge.settingFor('title') +\
        forge.settingFor('titledelimiter') +\
        forge.pageInfoFor(pagekey).get('title')

def makeStarterKit(forge, pagekey, template_filename = 'index.html'):
    """Executes boilerplate common to every page method
    
    Returns a 3-tuple of the page definition,
    the root soup object,
    and __change partially applied with the root soup"""
    soup = templateSoupFor(forge, template_filename)
    navlist = makeNavList(forge, pagekey)
    pagedef = forge.pageInfoFor(pagekey)
    change = partial(change_element, soup)
    dt = datetime.now()
    #select('title').string = makePageTitle(forge, pagekey)
    change('title', replaceString(makePageTitle(forge, pagekey)))
    change('.sitetitle', replaceString(forge.sitesettings['name']))
    change('a.rootlink', replaceHref('/' + forge.pageInfoFor('Home')['url']))
    change('.navbar ul', replaceWith(navlist))
    copyrightholder = forge.settingFor('copyrightholder', 'name')
    change('.copyright', replaceString('(c) ' + str(dt.year) + ' ' + copyrightholder))
    return (pagedef, soup, change)

def change_element(soup, selector, deltafn):
    """Convienence function to make *safely* changing a group of elements a one-liner

    Keyword Arguments:
    soup -- The parent bs4 element on which .select or .select_one will be called
    selector -- String css selector that selects a group of elements
    deltafn -- Function accepting a single element, that mutates the element as desired"""
    try :
        select = soup.select
        elements = select(selector)
        for element in elements:
            deltafn(element)
    except Exception as exp:
        print("Non-fatal problem: " + str(exp))

def replaceContents(newContents):
    """For use with change_element, shortcut for clearing and then appending on an element"""
    def retFn(element):
        element.clear()
        element.append(newContents)
    return retFn

def replaceWith(replacement):
    def retFn(element):
        element.replaceWith(replacement)
    return retFn

def replaceString(newString):
    """For use with change_element, shortcut for replacing the .string on an element"""
    def retFn(element):
        element.string.replaceWith(newString)
    return retFn

def replaceHref(newHref):
    """For use with change_element, shortcut for replacing the ['href'] on an element"""
    def retFn(element):
        element['href'] = newHref
    return retFn

def appendWith(additionalElement):
    """For use with change_element, shortcut for calling .append(additionalElement) on an element"""
    def retFn(element):
        element.append(additionalElement)
    return retFn

def previous_and_next(some_iterable):
    """https://stackoverflow.com/a/1012089"""
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

"""As html5lib does things a bit differently then other html parsers,
changing this is not advised without rewriting some of the functions in this module"""
__bs4parser__ = 'html5lib'
