from json import dumps, loads
from pyatom import AtomFeed
from wurmpages import * 

def makeBlogPage(forge, pagekey):
    """Page method for 'blog' page type"""
    pagedef, soup, change = makeStarterKit(forge, pagekey)
    rendermap = {}
    posts = grabBlogPosts(forge, pagekey)
    posts.sort(key = lambda x: x['date'])
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
    rendermap.update(makeBlogOverview(forge, pagekey, postsWithoutTag(posts, pagedef["hidetag"]), pagedef['url']))
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
    change('.tags', replaceWith(tagul))
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
    change('.pagetitle', replaceWith(pagedef['title']))
    change('.pagesubtitle', replaceWith(pagedef['subtitle']))

    for post in posts:
        slot = ___makeBlogOverviewSlot(forge, pagekey, post, copy(previewtemplate))
        change('.pagecontent', appendWith(slot))
    feeds = __makeFeedsForOverview(forge, pagekey, posts, url)
    return {trueurl : str(soup), **feeds}

def __makeFeedsForOverview(forge, pagekey, posts, url):
    if forge.settingFor('address'):
        filename = 'atom.xml'
        relpath = url + '/' + filename
        feedurl = forge.settingFor('address') + '/' + relpath
        pagedef = forge.pageInfoFor(pagekey)
        feed = AtomFeed(title=pagedef['title'],
                        subtitle=pagedef['subtitle'],
                        feed_url=feedurl,
                        url = url,
                        author = pagedef['author']) 
        for postdef in posts:
            feed.add(title=postdef['title'],
                     content=str(postdef['soup']),
                     content_type = 'xhtml',
                     author=postdef['author'],
                     url=forge.settingFor('address') + makePostUrl(pagedef, postdef),
                     updated=datetime.fromisoformat(postdef['date']))
        return {relpath: feed.to_string()}
    else:
        return {}

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

def previous_and_next(some_iterable):
    """https://stackoverflow.com/a/1012089"""
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)

def makeTagUL(forge, pagekey, tags):
    """Returns a bs4 ul element equivilant to
    <ul class="tags">
        <li><a href="/path/to/tag/summary">Tag Name</a></li>
    </ul>"""
    blankbody = BeautifulSoup('', bs4parser)
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




