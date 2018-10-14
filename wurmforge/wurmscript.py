from os import listdir, path, getcwd
from urllib.parse import quote, urlparse
import re
import sys
from importlib import import_module
from contextlib import suppress

def findpagemethod(forge, pluginpath):
    ns = import_module(pluginpath)
    return ns.pagemethod

def loadplugins(forge):
    sys.path.append(getcwd())
    plugin_list = findplugins(forge)
    pluginresults = execplugins(forge, plugin_list)
    for pagekey, pagemethod in pluginresults.items():
        forge.defPageMethod(pagekey, pagemethod)
    return pluginresults

def findplugins(forge):
    scripts_ls = listdir('plugins')
    script_paths = list(map(lambda a: 'plugins/'  + a, scripts_ls))
    plugin_list = list(filter(
        lambda potentialdir: path.isdir(potentialdir), 
        script_paths
    ))
    return plugin_list

def execplugins(forge, plugin_list):
    results = {}
    for plugindir in plugin_list:
        pluginpath = plugindir.replace('/', '.') + '.plugin'
        try:
            pagemethod = findpagemethod(forge, pluginpath)
            results.update({plugindir: pagemethod})
        except Exception as ex:
            if forge.debug_flag:
                print('Problem loading plugin: ' + str(ex))
            else:
                print("Problem loading plugin in " + plugindir)
    return results



