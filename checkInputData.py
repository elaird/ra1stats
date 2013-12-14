#!/usr/bin/env python

import data
import os
import sys


def check(topDir, subDir, fileName):
    if len(fileName) < 3 or fileName[-3:] != ".py":
        return

    module = fileName[:-3]
    if module in ["__init__"]:
        return

    try:
        exec("from %s.%s import %s" % (topDir, subDir, module))
    except:
        print module
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
            print module, item
            sys.excepthook(*sys.exc_info())
            print
            return False


def walk(top="", topSkip=[]):
    passed = []
    failed = []
    for dirName in os.listdir("%s/" % top):
        if dirName.startswith("__init__") or dirName.startswith("syst") or dirName in topSkip:
            continue

        print "%s:" % dirName
        for fileName in os.listdir("%s/%s" % (top, dirName)):
            if fileName == "__init__.py" or fileName.endswith(".pyc"):
                continue
            t = (top, dirName, fileName)
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


report(*walk(top="inputData", topSkip=["data2011old"]))
