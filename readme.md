# Wurmforge

A terminal (command-line) program that transforms json and markdown into a static site

# Use

` wurmforge target/dir ` (defaults to current directory)

Flag

| flag | long        | description                                                      |
| ---- | ----------- | ---------------------------------------------------------------- |
| `-d` | `--debug`   | Program emits stack traces and other debugging information       |
| `-p` | `--plugins` | Program runs plugins from /plugins. Without flag, no plugins run |

# Quickstart

1. From [releases](https://github.com/blakwurm/blaksite/releases), download the executable for your OS and the 'sample_project.zip' file
2. Unzip 'sample_project.zip' into your project folder
3. place executable in project folder
4. run executable

# Project Setup

A project directory consists of a sitesettings.json file, several directorys the program will use as input,
and somewhere that the program will put the finished site.

## Project Structure

| File/Directory | sitesettings key   | Description                                                                      |
| -------------- | ------------------ | -------------------------------------------------------------------------------- |
| /template      | "templatelocation" | Location of the site's template. contents (excpet /html) copied to output        |
| /media         | "medialocation"    | Location of the site's raw files. Directories under "pages" are relative to this |
| /assets        | "assetlocation"    | Location of the site's asset files. Copied to output directory                   |
| /plugins | n/a | Location of plugins that are loaded when the `-p` flag is used |
| output         | "output"           | Directory where the program will output the finished site. Default is 'docs'     |

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
| address          | Primary http/s address from which the site can be addressed.            | ''                              |
| output           | See [Project Structure](#project-structure)                             | docs (for github pages support) |
| medialocation    | See [Project Structure](#project-structure)                             | media                           |
| templatelocation | See [Project Structure](#project-structure)                             | template                        |
| assetslocation   | See [Project Structure](#project-structure)                             | assets                          |
| copyrightholder  | Used for the copyright line at the bottom of each page                  | value of 'name'                 |
| pageorder        | List of page keys in the order desired for the site's top-level nav bar | none                            |
| pages            | Map of one-word key to page specification. More information below       | none                            |

## Pages

Each entry in the pages map is a map of information

There must be a page under the "Home" key

| Key   | Description                                                                                |
| ----- | ------------------------------------------------------------------------------------------ |
| type  | Determines what information is required and how the page will be processed                 |
| title | Displayed in the page's title, after the delimiter                                         |
| url   | Directory where the site will be served from. At least one page must be the '' directory. |

### 'simple'

Uses 'template/index.html' as template file

| Key      | Description                                                                                                    |
| -------- | -------------------------------------------------------------------------------------------------------------- |
| source   | Path within the 'media' directory pointing to a markdown file, that will be rendered and displayed on the page |
| subtitle | Displayed on the page as the site's subtitle                                                                   |

### 'blog'

Uses 'template/blogpost.html' and 'template/blogsummary.html' as template files

If the 'address' field in sitesettings is not empty, an atom feed will be generated for the blog and each tag.

| Key           | Description                                                                                                                     |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| subtitle      | Displayed on the page as the site's subtitle                                                                                    |
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

### 'external'

Produces no pages, simply puts an external link into the navbar.

| Key | Description                                                                      |
| --- | -------------------------------------------------------------------------------- |
| url | External URL. Must begin with a protocol identifier like 'http://' or 'https://' | 

# Developing Templates 

Template files used by this program are complete HTML files. The template engine uses css selectors to manipulate the document,
eliminating the need for weird templating placeholders and allowing template designers to generate final template files without a content replacement step.

This does mean, however, that certain elements must be present within the document.

Note: These rules are applied for all elements matching a given selector

## Used by all templates

| Selector     | Use                                                                                                 |
| ------------ | --------------------------------------------------------------------------------------------------- |
| title        | Contents replaced by computed title                                                                 |
| a.rootlink   | href replaced with the url of the "Home" page                                                       |
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
# Developing Plugins

When the program is run with the `-p` flag, the project directory is added
to the system path, then for each subdirectory of /plugins, it will attempt 
to import plugins.foldername.plugin and get from it a function called 
'pagemethod'. This method will be registered under the
pagetype 'plugins/foldername', and will be dispatched to build pages
that use this as their 'type'. Plugins cannot assume that they are under
a spcific page type, as the program's user may decide to reorganize
the plugin directory to accomidate similar plugins

Each 'pagemethod' must be a two-arity function, with the parameters:
1. An instance of the WurmForge object
2. The key for the page in sitesettings['pages']
and that returns a dict of {path page is served from: string of file contents}

Note that a plugin's working directory is the root of the project 
directory. This means that plugins have full access to /template 
and /media. 

Also note that a plugin has full access to the wurmpages module, which
includes several functions to help construct pages from templates.

For an example plugin, see test/plugins/profile. This plugin is also provided in sample_project.zip

# Developing the tool

Requirements: Python 3.7 or greater

Setup: Clone the repository, and run pip install -r requirements.txt within the repo directory.

Running: Execute runtest/runtest.bat, and check 'test/docs'. This *does not* run unit tests, but rather executes
the program in debug mode against the test directory as a project. Unit tests are somewhat overkill for this program,
as checking for accuracy can easily be done by examining the app's output *and* the output
is complex enough that detailed unit tests will themselves be difficult to maintain.

Any new functionality must have a corresponding example in the test project.

This project does not use semver. After v1.0 launches, functionality will be locked,
and new versions will never break compatability. Note that this project *is* in alpha, so functionality
and the plugin api is still not locked down.

[A good talk on breakage, though not 100% relivant to Python and a liiiiitle long winded](https://www.youtube.com/watch?v=oyLBGkS5ICk)

## Building

Run __make.py from within the repo directory. This outputs the executable for your platform, as well as sample_project.zip, into 'dist/'
