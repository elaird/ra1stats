#!/usr/bin/env python

import data
import os
import sys


def check(topDir, fileName):
    if len(fileName) < 3 or fileName[-3:] != ".py":
        return

    module = fileName[:-3]
    if module in ["__init__"]:
        return

    exec("from %s import %s" % (topDir, module))
    for item in dir(eval(module)):
        if item == "data":
            continue
        obj = eval("%s.%s" % (module, item))
        if type(obj) != type:
            continue
        try:
            a = obj()
        except:
            print module, item
            sys.excepthook(*sys.exc_info())
            print


def walk(topDir=""):
    for dirName in os.listdir("%s/" % topDir):
        if dirName.startswith("__init__") or dirName.startswith("syst"):
            continue

        print dirName, ":"
        for fileName in os.listdir("%s/%s" % (topDir, dirName)):
            print fileName
            check(topDir, fileName)


walk("inputData")
