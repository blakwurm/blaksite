#!/usr/bin/python3
from os import system
from shutil import make_archive, rmtree, move
from contextlib import suppress

def main():
    with suppress(Exception):
        rmtree('dist')
        rmtree('build')
        rmtree('test/docs')
    system('pyinstaller wurmforge/__main__.py --onefile --clean --name "wurmforge" --icon=blakwurmlogo.ico')
    make_archive('dist/sample_project', format='zip', root_dir='test')
    
if __name__ == '__main__':
    import plac; plac.call(main)