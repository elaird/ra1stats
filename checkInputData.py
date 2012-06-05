#!/usr/bin/env python
import data,os,sys

def check(fileName) :
    if len(fileName)<3 or fileName[-3:]!=".py" : return
    module = fileName[:-3]
    if module in ["__init__", "syst"] : return

    exec("from input import %s"%module)
    for item in dir(eval(module)) :
        if item=="data" : continue
        obj = eval("%s.%s"%(module,item))
        if type(obj)!=type : continue
        try :
            a = obj()
        except:
            print module,item
            sys.excepthook(*sys.exc_info())
            print

def walk(topDir = "") :
    for dirName in os.listdir("%s/"%topDir) :
        print dirName,":"
        for fileName in os.listdir("%s/%s"%(topDir, dirName)) :
            print fileName
            check(fileName)


walk("inputData")
