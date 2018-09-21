#!/usr/bin/python3
from html.parser import HTMLParser
from json import dumps, loads

def getSiteOpts(siteopts_location):
    return loads(open(siteopts_location).read())

def main(siteopts: ("Site Config File" "option" "s") = "siteopts.json"):
    print("This is hello world!")
    print(getSiteOpts(siteopts)['pages'][1])

if __name__ == '__main__':
    import plac; plac.call(main)
