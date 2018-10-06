from bs4 import BeautifulSoup
from gfm import gfm, markdown
from json import dumps, loads
from copy import copy
from urllib.parse import quote
from re import compile
from contextlib import suppress
from itertools import tee, islice, chain


def makeSimplePage(forge, pagekey):
    for i in forge.prog(['a'], 'Making ' + pagekey):
        pagedef, soup = makeStarterKit(forge, pagekey)
        select = soup.select_one
        md1 = strainMarkdown(forge, pagedef['source'])
        pagemain = select('.pagecontent')
        pagemain.clear()
        pagemain.append(md1)
        select('.pagetitle').string = pagedef['title']
        select('.pagesubtitle').string = pagedef['subtitle']
    return {pagedef['url']: str(soup)}

def makeBlogPage(forge, pagekey):
    pagedef, soup = makeStarterKit(forge, pagekey)
    select = soup.select_one
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
    return forge.sitesettings['pages'][pagekey]['url'] + '/tag/' + tag

def makeBlogPost(forge, pagekey,
        postdef = {},
        formerpostdef = {},
        nextpostdef = {}):
    pagedef, soup = makeStarterKit(forge, pagekey, 'blogpost.html')
    select = soup.select_one
    soup.head.title.string = soup.head.title.string +\
            " - " + postdef['title']
    pagetitle = postdef['title']
    with suppress(Exception):
        select('.taglist').ul.\
                replace_with(makeTagUL(forge, pagekey, pagedef['tags']))
    with suppress(Exception):
        h1 = postdef['soup'].h1.extract()
        pagetitle = h1.string
    tagul = makeTagUL(forge, pagekey, postdef['tags'])
    select('.taglist').ul.replace_with(tagul)

    select('.pagetitle').string = pagetitle
    postsoup = postdef['soup']
    pagemain = select('.pagecontent')
    pagemain.clear()
    pagemain.append(postdef['soup'])
    select('.previouspost')['href'] =\
            formerpostdef['url'] if formerpostdef else postdef['url']
    select('.nextpost')['href'] =\
            nextpostdef['url'] if nextpostdef else postdef['url']
    select('.postdate').string = postdef['date'] 
    return {postdef['url']: str(soup)}

def postsWithTag(posts, tag):
    return [post for post in posts if tag in post['tags']]

def postsWithoutTag(posts, tag):
    return [post for post in posts if tag not in post['tags']]

def getTagsIn(forge, posts):
    retList = []
    for post in forge.prog(posts, 'Getting tags from posts'):
        retList.extend(post['tags'])
    return retList

def makeBlogOverview(forge, pagekey, posts = [], url = ''):
    pagedef, soup = makeStarterKit(forge, pagekey, "blogsummary.html")
    trueurl = url or pagedef['url']
    select = soup.select_one
    previewtemplate = select('.postpreview').extract()
    select('.taglist').ul.replace_with(makeTagUL(forge, pagekey, pagedef['tags']))
    def newTemplate():
        return copy(previewtemplate)
    for post in posts:
        slot = makeBlogOverviewSlot(forge, pagekey, post, newTemplate())
        select('.pagecontent').append(slot)
    return {trueurl : str(soup)}

def makeBlogOverviewSlot(forge, pagekey, post, template):
    pagedef = forge.sitesettings['pages'][pagekey]
    select = template.select_one
    select('.posttitle').string = post['title']
    select('.byline').string = post['author']
    select('.date').string = post['date']
    select('.preview').string = post['soup'].p.string
    select('.tags').replace_with(makeTagUL(forge, pagekey, post['tags']))
    for a in template.select(".continue"):
        a['href'] = post['url']
    return template

def makeMediaLink(forge, filename):
    return forge.sitesettings['medialocation'] + "/" + "filename"

def soupFor(forge, filename):
    with open("template/" + filename) as templatefile:
        return BeautifulSoup(templatefile, __bs4parser__)

def grabBlogPosts(forge, pagekey):
    pagesettings = forge.sitesettings['pages'][pagekey]
    postspath = pagesettings['postslocation']
    mediapath = forge.sitesettings['medialocation']
    postslocation = mediapath + '/' + postspath 
    postsdefs = getPostDefs(postslocation)
    for postdef in forge.prog(postsdefs, 'Processing ' + pagekey + ' posts'):
        processPostDef(postslocation, pagesettings, postdef)
    return postsdefs

def removeSpecialChars(title):
    reg = compile('[^a-zA-Z0-9]')
    return reg.sub('', title)
        
def makePostUrl(pagedef, post):
    return '/' + pagedef['url'] + '/post/' +\
            post['date'] + '/' + removeSpecialChars(post['title'])

def processPostDef(postslocation, pagedef, postdef):
    with open(postslocation + "/" + postdef['source']) as mdfile:
        postSoup = markdownToSoup(mdfile.read())
        postdef['soup'] = postSoup
        postdef['url'] = makePostUrl(pagedef, postdef)
        return postdef

def getPostDefs(postslocation):
    with open(postslocation + '/' + 'posts.json') as postsdef:
        return loads(postsdef.read())

def markdownToSoup(markdownstring):
    renderedMarkdown = markdown(gfm(markdownstring))
    newsoup = BeautifulSoup(renderedMarkdown, __bs4parser__)
    container = newsoup.body
    container.name = 'span'
    container['class'] = 'mdrender'
    return container

def strainMarkdown(forge, markdown_location):
    with open(forge.sitesettings['medialocation'] 
            + '/' + markdown_location, 'r') as markdownfile:
        return markdownToSoup(markdownfile.read())

def makeNavList(forge, pageOn):
    siteopts = forge.sitesettings
    blankbody = BeautifulSoup('', __bs4parser__)
    pageorder = forge.sitesettings['pageorder']
    ul = blankbody.new_tag(name='ul')
    #ul['class'] = ['navbar']
    for page in pageorder:
        pagedata =forge.sitesettings['pages'][page]
        li = blankbody.new_tag(name='li')
        if pageOn == page:
            li['class'] = ["hello"]
        a = blankbody.new_tag(name='a', href='/' + pagedata['url'])
        a.append(pagedata['title'])
        li.append(a)
        ul.append(li)
    return ul

def makeTagUL(forge, pagekey, tags):
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
    return forge.sitesettings['title'] +\
        forge.sitesettings['titledelimiter'] +\
        forge.sitesettings['pages'][pagekey]['title']

def makeStarterKit(forge, pagekey, template_filename = 'index.html'):
    soup = soupFor(forge, template_filename)
    navlist = makeNavList(forge, pagekey)
    pagedef = forge.pageInfoFor(pagekey)
    select = soup.select_one
    select('title').string = makePageTitle(forge, pagekey)
    select('.sitetitle').string = forge.sitesettings['name']
    select('.navbar').ul.replace_with(navlist)
    return (pagedef, soup)


def previous_and_next(some_iterable):
    "https://stackoverflow.com/a/1012089"
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

__bs4parser__ = 'html5lib'
