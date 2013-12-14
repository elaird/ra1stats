#!/usr/bin/env python

import os
import sys


def check(subDir, fileName):
    if len(fileName) < 3 or fileName[-3:] != ".py":
        return

    module = fileName[:-3]
    if module in ["__init__"]:
        return

    try:
        exec("from %s import %s" % (subDir, module))
    except:
        print subDir, module
        sys.excepthook(*sys.exc_info())
        print
        return False

    for item in dir(eval(module)):
        if item == "data":
            continue
        obj = eval("%s.%s" % (module, item))
        if type(obj) != type:
            continue
        try:
            a = obj()
            return True
        except:
            print subDir, module, item
            sys.excepthook(*sys.exc_info())
            print
            return False


def walk(skip=[]):
    passed = []
    failed = []

    filePath = os.path.dirname(__file__)
    os.chdir(filePath)
    for dirName in os.listdir("."):
        if dirName in skip:
            continue
        if os.path.islink(dirName) or not os.path.isdir(dirName):
            continue
        for fileName in os.listdir(dirName):
            if fileName == "__init__.py" or fileName.endswith(".pyc"):
                continue
            t = (dirName, fileName)
            (passed if check(*t) else failed).append(t)
    return passed, failed


def report(passed=[], failed=[]):
    def dump(l=[]):
        for t in l:
            print "/".join(t)

    print "%d passed:" % len(passed)
    dump(passed)
    print "%d failed:" % len(failed)
    dump(failed)


import data
report(*walk(skip=["data2011old"]))
