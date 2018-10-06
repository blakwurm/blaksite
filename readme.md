# Blaksite

A terminal (command-line) program that transforms json and markdown into a static site

## Use

Evoke the program from within a project directory (folder). The easiest way to do this on Windows is to have the .exe file in the directory and double-click it. 
## Project Setup

A project directory consists of a sitesettings.json file, a directory for 'media' (blog posts, images, etc), a directory for the site's 'template', and somewhere that the program will put the finished site.

### sitesettings.json

Note- all directories in sitesettings.json should be written without any leading or ending '/'. EG, 'template/css/main.css' and not '/template/css/main.css'

Below is an explanation of the sitesettings.json requirements. Please refer to test/sitesettings.json for an example

| Key              | Description                                                             | Default                         |
| --- | --- | --- |
| name             | Name of the site or orginization                                        | Unnamed Site                    |
| tagline          | Site subtitle                                                           | Catchy Tagline!                 |
| title            | Used for the `<title>` element                                          | Untitled Site                   |
| titledelimiter   | Subpages are titled 'title' 'titledelimiter' 'subpagetitle'             | ' - '                           |
| output           | Directory where the program will output the site. Default is 'docs'     | docs (for github pages support) |
| medialocation    | Where the program will find images, blog post markdown, etc             | media                           |
| templatelocation | Where the program will find the template html and css the site uses     | template                        |
| copyrightholder  | Used for the copyright line at the bottom of each page                  | value of 'name'                 |
| pageorder        | List of page keys in the order desired for the site's top-level nav bar | none                            |
| pages            | Map of one-word key to page specification. More information below       | none                            |

### Pages

Each entry in the pages map is a map of information

| Key  | Description                                                                |
| ---- | -------------------------------------------------------------------------- |
| type | Determines what information is required and how the page will be processed |

Type: 'simple'

| Key      | Description                                                                                                    |
| -------- | -------------------------------------------------------------------------------------------------------------- |
| source   | Path within the 'media' directory pointing to a markdown file, that will be rendered and displayed on the page |
| title    | Displayed in the page's title, after the delimiter                                                             |
| subtitle | Displayed on the page as the site's subtitle                                                                   |
| url      | Directory where the site will be served from. At least one page must be the '/' directory.                     |


