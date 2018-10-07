# Wurmforge

A terminal (command-line) program that transforms json and markdown into a static site

# Use

Evoke the program from within a project directory (folder). The easiest way to do this on Windows is to have the .exe file in the directory and double-click it. 

# Project Setup

A project directory consists of a sitesettings.json file, a directory for 'media' (blog posts, images, etc), a directory for the site's 'template', and somewhere that the program will put the finished site.

## sitesettings.json

Notes:
- All directories in sitesettings.json should be written without any leading or ending '/'. EG, 'template/css/main.css' and not '/template/css/main.css'
- For any page primarily rendering a markdown document, the first top-level header (eg '# Whatever') will be used as a replacement for the site's title

Below is an explanation of the sitesettings.json requirements. Please refer to test/sitesettings.json for an example

| Key              | Description                                                             | Default                         |
| ---------------- | ----------------------------------------------------------------------- | ------------------------------- |
| name             | Name of the site or orginization                                        | Unnamed Site                    |
| tagline          | Site subtitle                                                           | Catchy Tagline!                 |
| title            | Used to compute site title                                              | Untitled Site                   |
| titledelimiter   | Subpages are titled 'title' 'titledelimiter' 'subpagetitle'             | ' - '                           |
| output           | Directory where the program will output the site. Default is 'docs'     | docs (for github pages support) |
| medialocation    | Where the program will find images, blog post markdown, etc             | media                           |
| templatelocation | Where the program will find the template html and css the site uses     | template                        |
| copyrightholder  | Used for the copyright line at the bottom of each page                  | value of 'name'                 |
| pageorder        | List of page keys in the order desired for the site's top-level nav bar | none                            |
| pages            | Map of one-word key to page specification. More information below       | none                            |

## Pages

Each entry in the pages map is a map of information

| Key  | Description                                                                |
| ---- | -------------------------------------------------------------------------- |
| type | Determines what information is required and how the page will be processed |

### 'simple'

Uses 'template/index.html' as template file

| Key      | Description                                                                                                    |
| -------- | -------------------------------------------------------------------------------------------------------------- |
| source   | Path within the 'media' directory pointing to a markdown file, that will be rendered and displayed on the page |
| title    | Displayed in the page's title, after the delimiter                                                             |
| subtitle | Displayed on the page as the site's subtitle                                                                   |
| url      | Directory where the site will be served from. At least one page must be the '/' directory.                     |

### 'blog'

Uses 'template/blogpost.html' and 'template/blogsummary.html' as template files

| Key           | Description                                                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| title         | Displayed in the page's title, after the delimiter                                                                              |
| subtitle      | Displayed on the page as the site's subtitle                                                                                    |
| url           | Directory where the site will be served from. At least one page must be the '/' directory.                                      |
| author        | Main maintainer of the site. Used when 'author' is missing from post entry                                                      |
| postslocation | Path within the 'media' directory where posts.json can be found                                                                 |
| hidetag       | Posts with this tag will not be shown on the main blog overview. This tag will still be shown in the 'tags' section of the blog |

#### posts.json

At the root of the blog's 'postslocation', there should be a posts.json file consisting of a list of maps representing blog posts. Order does not matter.

Each post must have the following information

| Key    | Description                                                                                                       |
| ------ | ----------------------------------------------------------------------------------------------------------------- |
| date   | The date of the post, written in 'YYYY-MM-DD' (ISO 8601). Used for the URL as well as for post sorting.           |
| title  | Title of the post, used for the URL and displayed in the title of the post.                                       |
| author | The author of the post.                                                                                           |
| source | A path relative to the folder containing posts.json, pointing to a markdown file containing the body of the post. |
| tags   | A list of tags applicable to the post, used to organize posts and displayed as metadata along with each post.     |

# Developing Templates 

Template files used by this program are complete HTML files. The template engine uses css selectors to manipulate the document,
eliminating the need for weird templating placeholders and allowing template designers to generate final template files without a content replacement step.
This does mean, however, that certain elements must be present within the document.

Note: Unless otherwise specified, only the first instance of each element in the document will be processed. 

## Used by all templates

| Selector     | Use                                                                                                 |
| ------------ | --------------------------------------------------------------------------------------------------- |
| title        | Contents replaced by computed title                                                                 |
| .sitetitle   | Contents replaced by 'name' from sitesettings                                                       |
| .sitetagline | Contents replaced by 'tagline' from sitesettings                                                    |
| .navbar ul   | Element replaced by a ul of `<li><a href="/page/path">Page Name</a></li>`, creating site navigation |
| .pagemain    | Container for content, handled differently depending on the template                                |
| .pagetitle   | Contents replaced by computed page title                                                            |
| .copyright   | Contents replaced by the computed copyright statement                                               |

## index.html

| Selector      | Use                                                |
| ------------- | -------------------------------------------------- |
| .pagesubtitle | Contents replaced by computed page subtitle        |
| .pagecontent  | Contents replaced by contents of rendered markdown |

## blogpost.html 

| Selector       | Use                                                                                                                                                |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| .postdate      | Contents replaced by date of post                                                                                                                  |
| .pagecontent   | Contents replaced by contents of rendered markdown                                                                                                 |
| .taglist ul    | Element replaced by a ul with class 'tags' of `<li><a href="/path/to/tag/overview">Tag</a></li>` of the tags for the post, creating tag navigation |
| a.previouspost | href replaced by path to previous blog post                                                                                                        |
| a.nextpost     | href replaced by path to next blog post                                                                                                            |

## blogsummary.html

| Selector      | Use                                                                                                                                            |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| .pagesubtitle | Contents replaced by computed page subtitle                                                                                                    |
| .pagecontent  | Contents cleared, computed post previews inserted                                                                                              |
| .postpreview  | First instance removed from .pagecontent, duplicated and used as the template for all previews on the page                                     |
| .taglist ul   | Element replaced by a ul with class of `<li><a href="/path/to/tag/overview">Tag</a></li>` of all the tags in the blog, creating tag navigation |

Within .postpreview, not necessarily as direct children

| Selector   | Use                                                                                                                                         |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| .date      | Contents replaced by post date                                                                                                              |
| .continue  | href replaced by path to post page. Multiple instances processed                                                                            |
| .posttitle | Contents replaced by post title                                                                                                             |
| .byline    | Contents replaced by post author                                                                                                            |
| .tags      | Element replaced by a ul with class of `<li><a href="/path/to/tag/overview">Tag</a></li>` of the tags for the post, creating tag navigation |
| .preview   | Contents replaced by the first paragraph of the blog post                                                                                   |

# Developing the tool

This tool requires at least Python 3.5 to be installed on the dev system. 

Clone the repository, and run pip install -r requirements.txt within the repo directory.

Run the code by executing the 'run' script within the 'test' directory. This *does not* run unit tests, but rather executes the program against the test directory as if it were a project.

Any new functionality must have a corresponding example in the test project.

## Building

Both 'compile' and 'compile.bat' have the preferred command for building. At this time, PyInstaller is the preferred method for packing this program for distribution.

The current test directory can serve as an adaquate template for new projects, though one prepared for consumption with a proper release is preferred.