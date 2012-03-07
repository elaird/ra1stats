#!/usr/bin/env python
import data,os

for fileName in os.listdir("inputData/") :
    if len(fileName)<3 or fileName[-3:]!=".py" : continue
    module = fileName[:-3]
    if module in ["__init__", "syst"] : continue

    exec("from inputData import %s"%module)
    for item in dir(eval(module)) :
        if item=="data" : continue
        obj = eval("%s.%s"%(module,item))
        if type(obj)!=type : continue
        try :
            a = obj()
        except:
            print module,item

