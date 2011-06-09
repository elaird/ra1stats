#!/usr/bin/env python

from inputData import data2011

data = data2011()

print "HT bins"
print "-------"
print data.htBinLowerEdges()
print

for item in ["lumi", "observations", "mcExpectations", "fixedParameters"] :
    print item
    print "-"*len(item)
    d = getattr(data,item)()
    for key,value in d.iteritems() :
        if item=="lumi" and ("mc" in key) : continue
        if type(value)!= tuple :
            print key,value
        else :
            print key,tuple([value[0], value[1], sum(value[2:])])
    print
