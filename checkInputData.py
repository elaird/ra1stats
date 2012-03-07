#!/usr/bin/env python
import data

for module in ["afterAlphaT", "afterAlphaT_b", "mixedMuons", "mixedMuons_b_sets", "orig", "afterAlphaT_noMHT_ov_MET", "mixedMuons_b", "mixedMuons_b_sets_aT", "simpleOneBin"] :
    exec("from inputData import %s"%module)
    for item in dir(eval(module)) :
        if item=="data" : continue
        obj = eval("%s.%s"%(module,item))
        if type(obj)!=type : continue
        try :
            a = obj()
        except:
            print module,item

