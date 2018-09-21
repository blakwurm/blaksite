#!/usr/bin/python3
from html.parser import HTMLParser
from json import dumps, loads

def main():
    print("This is hello world!")
    print(loads(open("siteopts.json").read())['pages'][1])

if __name__ == '__main__':
    import plac; plac.call(main)
